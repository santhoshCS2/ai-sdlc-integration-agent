"""
PlannerAgent - Converts user prompt into detailed spec, user stories, API endpoints
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.coding.utils.logger import StreamlitLogger

class PlannerAgent:
    """Agent that creates detailed project specifications"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def create_spec(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed project specification"""
        self.logger.log("📋 Analyzing requirements and creating project specification...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an senior enterprise software architect. Your task is to analyze a project description and create a comprehensive, PRODUCTION-READY technical specification.
            
            🚨 PROFESSIONAL STANDARDS:
            1. EXCLUDE all "demo", "sample", "mock", or "dummy" data/logic.
            2. Design for scalability, security, and maintainability.
            3. Use professional naming conventions (e.g., `UserService`, `AuthRepository`).
            4. Real-world API design: Include pagination, filtering, and proper error handling.
            5. Enterprise DB design: Proper foreign keys, indexing, and normalization.

Create a detailed specification including:
1. Project overview and goals (Professional tone)
2. User stories (Full-coverage, production-level)
3. API endpoints (RESTful) with strict request/response schemas
4. Database schema (Production-grade tables, relationships)
5. Authentication requirements (JWT/OAuth/Best practices)
6. Key features and functionality (Production features only)
7. Technical requirements (Enterprise stack requirements)

Return your response as a structured JSON object with the following structure:
{{
    "overview": "Project overview",
    "user_stories": ["story1", "story2", ...],
    "api_endpoints": [
        {{
            "method": "GET|POST|PUT|DELETE",
            "path": "/api/v1/endpoint",
            "description": "Endpoint description",
            "request_body": {{"field": "type"}},
            "response": {{"field": "type"}}
        }}
    ],
    
    "database_schema": {{
        "tables": [
            {{
                "name": "table_name",
                "fields": [
                    {{"name": "field_name", "type": "string|integer|boolean|datetime", "required": true}}
                ],
                "relationships": []
            }}
        ]
    }},
    "authentication": {{
        "required": true,
        "method": "JWT|OAuth",
        "features": ["login", "register", "password_reset", "mfa"]
    }},
    "features": ["feature1", "feature2", ...],
    "technical_requirements": ["req1", "req2", ...]
}}"""),
            ("human", """Project Name: {project_name}
Description: {description}
Frontend Stack: {frontend_stack}
Backend Stack: {backend_stack}

Create a comprehensive technical specification for this project.""")
        ])
        
        try:
            messages = prompt.format_messages(
                project_name=project_config["project_name"],
                description=project_config["description"],
                frontend_stack=project_config["frontend_stack"],
                backend_stack=project_config["backend_stack"]
            )
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Parse JSON from response (handle markdown code blocks)
            import json
            import re
            
            # Method 1: Extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Method 2: Find JSON object directly (handle multiline carefully)
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    content = json_match.group(0)
            
            spec = json.loads(content)
            self.logger.log(f"✅ Created specification with {len(spec.get('user_stories', []))} user stories and {len(spec.get('api_endpoints', []))} API endpoints")
            
            return spec
            
        except Exception as e:
            error_str = str(e)
            self.logger.log(f"⚠️ Error creating spec: {error_str}", level="error")
            
            # Check if this is an API error that should trigger fallback
            if "402" in error_str or "requires more credits" in error_str.lower() or "can only afford" in error_str.lower():
                self.logger.log("🔄 OpenRouter credits insufficient, falling back to Groq...")
            
            # Retry once with a simpler prompt (will use fallback if available)
            try:
                self.logger.log("🔄 Retrying with simplified prompt...")
                simple_prompt = f"""Create a JSON specification for this project:

Project: {project_config['project_name']}
Description: {project_config['description']}
Frontend: {project_config['frontend_stack']}
Backend: {project_config['backend_stack']}

Return ONLY valid JSON with: overview, user_stories (array), api_endpoints (array), database_schema (object with tables array), authentication (object), features (array), technical_requirements (array)."""
                
                retry_response = self.llm.invoke([("user", simple_prompt)])
                content = retry_response.content.strip()
                
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    content = json_match.group(0)
                
                spec = json.loads(content)
                self.logger.log(f"✅ Created specification with retry")
                return spec
            except Exception as retry_error:
                # Only use minimal fallback if retry also fails
                self.logger.log("❌ Both attempts failed", level="error")
                raise Exception(f"Failed to generate project specification: {error_str}")

