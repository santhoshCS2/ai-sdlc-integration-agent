"""
FrontendAnalyzerAgent - Analyzes frontend code to discover API requirements
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from app.agents.coding.utils.logger import StreamlitLogger

class FrontendAnalyzerAgent:
    """Agent that analyzes frontend code to extract API specifications"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def analyze(self, frontend_code: Dict[str, str]) -> Dict[str, Any]:
        """Analyze frontend files to understand API needs"""
        if not frontend_code:
            self.logger.log("⚠️ No frontend code to analyze")
            return {}
            
        self.logger.log(f"🔍 Analyzing {len(frontend_code)} frontend files for API requirements...")
        
        # Filter for relevant files to avoid overwhelming the LLM
        relevant_files = {}
        for path, content in frontend_code.items():
            if any(ext in path for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue']):
                if 'node_modules' not in path and 'test' not in path:
                    # Keep only files that likely contain API logic or data structures
                    if any(term in content for term in ['fetch', 'axios', 'api', 'useEffect', 'useState', 'http']):
                        relevant_files[path] = content[:3000] # Cap size
        
        if not relevant_files:
            self.logger.log("⚠️ No relevant frontend files found for API analysis")
            return {}

        self.logger.log(f"📝 Found {len(relevant_files)} relevant files for deep analysis")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert full-stack architect. Analyze the provided frontend source code to extract requirements for a PROFESSIONAL BACKEND API.
            
            Identify:
            1. API Endpoints: Paths, methods (GET/POST/etc.), and their purposes.
            2. Data Structures: What fields are displayed? What fields are sent in forms?
            3. Authentication: How is the frontend currently handling auth (if at all)?
            4. Constants: API base URLs or environment variable usages.
            5. 🚨 DEMO CODE DETECTION: Flag any and all "mock", "dummy", "sample", or "test" data structures, hardcoded lists, or non-functional buttons.
            
            Return your findings as a structured JSON object:
            {{
                "endpoints": [
                    {{
                        "path": "/api/v1/users",
                        "method": "GET",
                        "description": "Used in UserProfile component to load data",
                        "inferred_fields": ["id", "username", "email"]
                    }}
                ],
                "data_models": {{
                    "User": ["id", "username", "email", "avatar"],
                    "Item": ["id", "title", "description", "price"]
                }},
                "auth_strategy": "Bearer token in localStorage",
                "observations": "Any other relevant details for backend generation",
                "demo_removal_hints": [
                    {{
                        "file": "src/components/UserList.jsx",
                        "type": "hardcoded_array",
                        "variable": "users",
                        "context": "Needs to be replaced with state populated from GET /api/v1/users"
                    }}
                ]
            }}
            """),
            ("human", "Analyze these frontend files:\n\n{files_content}")
        ])
        
        try:
            # Prepare file list for prompt
            files_summary = ""
            for path, content in list(relevant_files.items())[:20]: # Limit to 20 files
                files_summary += f"FILE: {path}\nCONTENT:\n{content}\n---\n"
            
            messages = prompt.format_messages(files_content=files_summary)
            self.logger.log("🤖 Calling LLM for frontend code analysis...")
            response = self.llm.invoke(messages, max_tokens=8000)
            content = response.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)
            
            analysis = json.loads(content)
            self.logger.log(f"✅ Extracted {len(analysis.get('endpoints', []))} endpoints from code analysis")
            
            return analysis
            
        except Exception as e:
            self.logger.log(f"⚠️ Error analyzing frontend code: {str(e)}", level="error")
            return {}
