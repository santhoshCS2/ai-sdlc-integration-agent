"""
BackendGeneratorAgent - Generates full backend (routes, models, auth, DB schema) for selected stack
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
import json
from app.agents.coding.utils.logger import StreamlitLogger

class BackendGeneratorAgent:
    """Agent that generates backend code"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def generate(self, project_spec: Dict[str, Any], backend_stack: str, project_config: Optional[Dict[str, Any]] = None, report_data: Optional[Dict[str, Any]] = None, frontend_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate backend code based on spec and analyzed report/frontend data"""
        self.logger.log(f"🔧 Generating {backend_stack} backend code from analyzed data...")
        
        # Use analyzed report data (preferred) or fall back to raw content
        impact_content = ""
        
        if report_data and report_data.get("content"):
            # Use the analyzed report content
            impact_content = report_data.get("content")
            analysis = report_data.get("analysis", {})
            
            # Add structured analysis to help LLM understand requirements better
            if analysis:
                impact_content = f"""ANALYZED REPORT DATA:

Project Overview: {analysis.get('project_overview', 'N/A')}

Key Requirements:
{chr(10).join('- ' + req for req in analysis.get('key_requirements', []))}

Backend Structure: {analysis.get('backend_structure', 'N/A')}

Technical Details: {analysis.get('technical_details', 'N/A')}

Data Models: {analysis.get('data_models', 'N/A')}

Integrations: {analysis.get('integrations', 'N/A')}

Security Notes: {analysis.get('security_notes', 'N/A')}

Performance Notes: {analysis.get('performance_notes', 'N/A')}

--- FULL REPORT CONTENT ---
{impact_content}
"""
            
            self.logger.log(f"✅ Using analyzed report data ({len(impact_content) if impact_content else 0} characters)")
        elif project_config:
            # Fallback to raw file content if report_data not available
            prd_content = project_config.get("prd_file_content")
            impact_file_content = project_config.get("impact_file_content")
            
            if prd_content:
                if isinstance(prd_content, bytes):
                    prd_text = prd_content.decode('utf-8', errors='ignore')
                else:
                    prd_text = str(prd_content)
                impact_content += f"PRD REQUIREMENTS:\n{prd_text}\n\n"
            
            if impact_file_content:
                if isinstance(impact_file_content, bytes):
                    impact_text = impact_file_content.decode('utf-8', errors='ignore')
                else:
                    impact_text = str(impact_file_content)
                impact_content += f"IMPACT ANALYSIS REQUIREMENTS:\n{impact_text}\n\n"
            
            self.logger.log(f"⚠️ Using raw file content as fallback ({len(impact_content)} characters)")
        
        if not impact_content:
            self.logger.log("⚠️ No Impact Analysis content found. Generating default backend structure...", level="warning")
            return self._generate_comprehensive_fallback(project_spec, backend_stack, project_config)
        
        self.logger.log(f"📝 Report content length: {len(impact_content)} characters")
        self.logger.log(f"🔍 Report preview: {impact_content[:300]}..." if len(impact_content) > 300 else f"🔍 Full report: {impact_content}")
        
        # Pre-analyze the report to extract API specifications
        extracted_specs = self._extract_api_specifications(impact_content)
        self.logger.log(f"📊 Extracted from report: {len(extracted_specs.get('endpoints', []))} endpoints, {len(extracted_specs.get('models', []))} models")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior lead backend architect. Your task is to generate a PRODUCTION-READY, ENTERPRISE-GRADE, MODULAR backend.

🚨 PROFESSIONAL ARCHITECTURAL RULES:
1. NO FLAT STRUCTURES: Use a strictly modular layout (routers/, models/, schemas/, services/, core/, db/).
2. 🚨 NO DEMO CODE: Absolutely EXCLUDE any "sample", "demo", "mock", or "dummy" data, comments, or logic.
3. CONFIGURATION: Use `pydantic-settings` for all configurations. NO hardcoded secrets.
4. API DESIGN: Implement EXACT professional endpoints from specifications using FastAPI APIRouter.
5. DATA INTEGRITY: Use SQLAlchemy for models and Pydantic for request/response schemas.
6. SECURITY: Include JWT authentication, password hashing (passlib/bcrypt), and strict CORS middleware.
7. DOCUMENTATION: Use type hints everywhere and include docstrings for all modules/classes.
8. DEPENDENCIES: Provide a comprehensive `requirements.txt` with specific version ranges.

DIRECTORY STRUCTURE:
- app/api/endpoints/ (Route handlers)
- app/models/ (SQLAlchemy models)
- app/schemas/ (Pydantic models)
- app/services/ (Business logic separation)
- app/core/ (Auth, Security, Settings)
- app/db/ (Database session management)
- main.py (Entry point)

YOU MUST:
- Search for and extract ALL endpoints, data structures, and business logic from the Impact Analysis.
- Generate COMPLETE code for every file. NO PLACEHOLDERS like "# Implement logic here".
- Ensure `__init__.py` files exist to make directories valid Python packages.

RETURN FORMAT:
You MUST return ONLY valid JSON with NO markdown, NO explanations, just pure JSON.
{{
    "app/core/config.py": "pydantic settings code",
    "app/api/endpoints/users.py": "complete router code",
    "app/models/user.py": "SQLAlchemy model code",
    "app/schemas/user.py": "Pydantic schema code",
    "main.py": "app setup code",
    "requirements.txt": "dependencies code"
}}
"""),
            ("human", """IMPACT ANALYSIS DOCUMENT:
{impact_content}

Project Specification:
{project_spec}

Frontend Analysis (Code Requirements):
{frontend_analysis}

Backend Stack: {backend_stack}

ANALYZE THE IMPACT ANALYSIS DOCUMENT AND FRONTEND CODE REQUIREMENTS ABOVE TO GENERATE THE EXACT BACKEND STRUCTURE SPECIFIED.

CRITICAL ANALYSIS TASKS:
1. FIND the backend file structure, directory layout, and organization mentioned in the Impact Analysis
2. IDENTIFY specific file names, paths, controllers, models, routes, and components described
3. LOCATE API endpoint specifications, database schema requirements, and business logic details
4. EXTRACT any specific technology choices, frameworks, libraries, or architectural patterns mentioned
5. NOTE any naming conventions, coding standards, file organization patterns specified

GENERATE REQUIREMENTS:
- CREATE the EXACT file structure and directory layout described in the Impact Analysis
- IMPLEMENT ALL files, components, and modules mentioned with COMPLETE functionality
- FOLLOW the precise naming conventions, file paths, and organization specified
- BUILD all API endpoints with full business logic as described in the document
- DEVELOP database models with all fields, relationships, and constraints mentioned
- INCLUDE all configuration, middleware, utilities, and supporting files specified
- USE the exact technology stack, frameworks, and libraries mentioned in the analysis

EXAMPLE: If the Impact Analysis mentions:
"The backend should have a controllers/ directory with userController.js and productController.js files"
"Database models should be in models/ directory with User.js and Product.js"
"Routes should be organized in routes/api/v1/ with separate files for each resource"

Then generate EXACTLY:
- controllers/userController.js (with complete implementation)
- controllers/productController.js (with complete implementation)  
- models/User.js (with full model definition)
- models/Product.js (with full model definition)
- routes/api/v1/users.js (with complete routing logic)
- routes/api/v1/products.js (with complete routing logic)

DO NOT create generic structures - follow the EXACT specifications from the Impact Analysis document.

Return ONLY the JSON object with complete, production-ready code that matches the Impact Analysis requirements precisely.""")
        ])
        
        # Retry logic to ensure we get LLM-generated code
        max_retries = 3
        for attempt in range(max_retries):
            try:
                messages = prompt.format_messages(
                    impact_content=impact_content + "\n\nEXTRACTED SPECIFICATIONS:\n" + json.dumps(extracted_specs, indent=2),
                    project_spec=json.dumps(project_spec, indent=2),
                    frontend_analysis=json.dumps(frontend_analysis, indent=2) if frontend_analysis else "N/A",
                    backend_stack=backend_stack
                )
                
                self.logger.log(f"🤖 Calling LLM to generate backend code (attempt {attempt + 1}/{max_retries})...")
                self.logger.log(f"📊 Sending {len(impact_content)} chars to LLM for analysis...")
                # Request higher token limit for complete backend generation
                response = self.llm.invoke(messages, max_tokens=16000)
                content = response.content.strip()
                
                # Clean content from common LLM garbage
                if content.startswith(("Here is", "Certainly", "Sure")):
                    # Try to find the first '{' and use everything from there
                    first_brace = content.find('{')
                    if first_brace != -1:
                        content = content[first_brace:]

                # Parse JSON from response - try multiple methods
                import re
                
                # Method 1: Extract from markdown code blocks
                json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                else:
                    # Method 2: Find JSON object directly
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        content = json_match.group(0)
                
                # Try to parse JSON
                backend_code = json.loads(content.strip())
                self.logger.log(f"✅ Successfully parsed JSON with {len(backend_code) if isinstance(backend_code, dict) else 0} entries")
                
                # Validate we got actual code files
                if not isinstance(backend_code, dict) or len(backend_code) < 5:
                    raise ValueError(f"LLM response contains only {len(backend_code) if isinstance(backend_code, dict) else 0} files, need at least 5")
                
                # Validate essential files are present
                essential_files = ['requirements.txt', 'main.py', 'models.py']
                missing_files = []
                for essential in essential_files:
                    if not any(essential in path for path in backend_code.keys()):
                        missing_files.append(essential)
                
                if missing_files:
                    raise ValueError(f"Missing essential files: {missing_files}")
                
                # Validate files have substantial content (not just imports)
                for file_path, content in backend_code.items():
                    if len(content.strip()) < 50:  # Very short files are likely incomplete
                        raise ValueError(f"File {file_path} appears incomplete (too short)")
                
                file_count = len(backend_code)
                self.logger.log(f"✅ Generated {file_count} complete backend files from LLM")
                
                # Log file names for debugging
                self.logger.log("Generated files:")
                for file_path in list(backend_code.keys())[:10]:  # Show first 10 files
                    self.logger.log(f"  - {file_path}")
                if len(backend_code) > 10:
                    self.logger.log(f"  ... and {len(backend_code) - 10} more files")
                
                return backend_code
                
            except json.JSONDecodeError as e:
                self.logger.log(f"⚠️ JSON parse error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Ask LLM to fix the JSON
                    fix_prompt = f"""The previous response had invalid JSON. Please fix it and return ONLY valid JSON.

Previous response (first 500 chars):
{content[:500]}

Error: {str(e)}

Return ONLY the corrected JSON object:"""
                    try:
                        fix_response = self.llm.invoke([("user", fix_prompt)])
                        content = fix_response.content.strip()
                        # Try parsing again
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            content = json_match.group(0)
                        backend_code = json.loads(content)
                        if isinstance(backend_code, dict) and len(backend_code) >= 3:
                            self.logger.log(f"✅ Generated {len(backend_code)} backend files after JSON fix")
                            return backend_code
                    except:
                        continue
                else:
                    self.logger.log(f"❌ Failed to parse JSON after {max_retries} attempts", level="error")
                    
            except Exception as e:
                self.logger.log(f"⚠️ Error generating backend (attempt {attempt + 1}/{max_retries}): {str(e)}", level="error")
                if attempt == max_retries - 1:
                    # Last attempt failed - try simplified generation
                    self.logger.log("⚠️ All LLM attempts failed. Generating fallback backend...", level="warning")
                    if len(impact_content) > 100:
                        return self._generate_from_extracted_specs(extracted_specs, backend_stack, project_spec)
                    else:
                        return self._generate_comprehensive_fallback(project_spec, backend_stack, project_config)
        
        # Final fallback if loop somehow exits without returning
        self.logger.log("⚠️ Backend generation loop completed without result. Delivering comprehensive fallback.", level="warning")
        return self._generate_comprehensive_fallback(project_spec, backend_stack, project_config)
    
    def _generate_comprehensive_fallback(self, project_spec: Dict[str, Any], backend_stack: str, project_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate comprehensive fallback backend when LLM fails"""
        self.logger.log(f"🔧 Generating comprehensive {backend_stack} fallback backend...")
        
        if "FastAPI" in backend_stack:
            return self._generate_fastapi_backend(project_spec, project_config)
        elif "Django" in backend_stack:
            return self._generate_django_backend(project_spec, project_config)
        elif "Node.js" in backend_stack or "Express" in backend_stack:
            return self._generate_nodejs_backend(project_spec, project_config)
        else:
            return self._generate_fastapi_backend(project_spec, project_config)  # Default to FastAPI
    
    def _generate_fastapi_backend(self, project_spec: Dict[str, Any], project_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate comprehensive FastAPI backend"""
        project_name = project_spec.get('overview', 'API').replace(' ', '_').lower()
        
        # Analyze impact analysis for specific file requirements
        required_files = self._analyze_impact_requirements(project_config)
        
        # Generate default API endpoints
        endpoints_code = """@app.get("/api/items")
def get_items(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Get all items
    try:
        items = db.query(Item).filter(Item.owner_id == current_user).all()
        return {"items": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/items")
def create_item(item_data: ItemCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Create new item
    try:
        new_item = Item(**item_data.dict(), owner_id=current_user)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {"item": new_item, "message": "Item created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
        
        base_files = {
            "app/__init__.py": "",
            "app/main.py": f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{{settings.API_V1_STR}}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
""",
            "app/core/config.py": f"""import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    API_V1_STR: str = "/api/v1"
    
    # These should be loaded from environment variables
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
""",
            "app/db/session.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
            "app/models/base.py": """from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
""",
            "app/models/item.py": """from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
""",
            "app/schemas/item.py": """from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True
""",
            "app/api/api.py": """from fastapi import APIRouter
from app.api.endpoints import items

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
""",
            "app/api/endpoints/items.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.item import Item as ItemModel
from app.schemas.item import Item, ItemCreate

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    items = db.query(ItemModel).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
""",
            "requirements.txt": """fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.7.4
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
""",
            "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        }
        
        # Add any additional files mentioned in impact analysis
        if required_files:
            base_files.update(required_files)
        
        return base_files
    
    def _analyze_impact_requirements(self, project_config: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze impact analysis content for specific file requirements"""
        additional_files = {}
        
        if not project_config:
            return additional_files
        
        # Get impact analysis content
        impact_content = ""
        prd_content = project_config.get("prd_file_content")
        impact_file_content = project_config.get("impact_file_content")
        
        if prd_content:
            if isinstance(prd_content, bytes):
                impact_content += prd_content.decode('utf-8', errors='ignore')
            else:
                impact_content += str(prd_content)
        
        if impact_file_content:
            if isinstance(impact_file_content, bytes):
                impact_content += impact_file_content.decode('utf-8', errors='ignore')
            else:
                impact_content += str(impact_file_content)
        
        if not impact_content:
            return additional_files
        
        self.logger.log(f"📊 Analyzing {len(impact_content)} characters for specific file requirements...")
        
        # Look for specific file mentions in the content
        import re
        
        # Common patterns for file mentions
        file_patterns = [
            r'create[\s\w]*file[\s\w]*[:"]\s*([\w\./]+\.\w+)',
            r'file[\s\w]*[:"]\s*([\w\./]+\.\w+)',
            r'([\w\./]+\.py)\s*[:-]',
            r'([\w\./]+\.js)\s*[:-]',
            r'([\w\./]+\.json)\s*[:-]',
            r'([\w\./]+\.yml)\s*[:-]',
            r'([\w\./]+\.yaml)\s*[:-]',
            r'([\w\./]+\.md)\s*[:-]',
            r'([\w\./]+\.txt)\s*[:-]',
            r'([\w\./]+\.env)\s*[:-]',
        ]
        
        found_files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, impact_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and len(match) > 2 and '.' in match:
                    found_files.add(match.strip())
        
        # Generate content for found files
        for file_path in found_files:
            if file_path not in ['main.py', 'models.py', 'schemas.py', 'database.py', 'auth.py', 'settings.py', 'requirements.txt']:
                # Generate appropriate content based on file type
                if file_path.endswith('.py'):
                    additional_files[file_path] = self._generate_python_file_content(file_path, impact_content)
                elif file_path.endswith('.json'):
                    additional_files[file_path] = self._generate_json_file_content(file_path, impact_content)
                elif file_path.endswith(('.yml', '.yaml')):
                    additional_files[file_path] = self._generate_yaml_file_content(file_path, impact_content)
                elif file_path.endswith('.md'):
                    additional_files[file_path] = self._generate_markdown_content(file_path, impact_content)
                else:
                    additional_files[file_path] = f"# {file_path}\n# Generated from impact analysis requirements\n"
        
        if additional_files:
            self.logger.log(f"📝 Generated {len(additional_files)} additional files from impact analysis")
            for file_path in additional_files.keys():
                self.logger.log(f"  - {file_path}")
        
        return additional_files
    
    def _generate_python_file_content(self, file_path: str, impact_content: str) -> str:
        """Generate Python file content based on file name and requirements"""
        file_name = file_path.split('/')[-1].replace('.py', '')
        
        if 'test' in file_name.lower():
            test_func_name = file_name.replace('test_', '')
            return f"""# {file_path}
# Test file generated from impact analysis requirements

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_{test_func_name}():
    \"\"\"Test function for {file_name}\"\"\"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
"""
        elif 'config' in file_name.lower():
            class_name = file_name.title().replace('_', '')
            return f"""# {file_path}
# Configuration file generated from impact analysis requirements

import os
from typing import Optional

class {class_name}Config:
    \"\"\"Configuration class for {file_name}\"\"\"
    
    def __init__(self):
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.environment = os.getenv('ENVIRONMENT', 'development')
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        \"\"\"Get configuration setting\"\"\"
        return os.getenv(key, default)

config = {class_name}Config()
"""
        else:
            class_name = file_name.title().replace('_', '')
            return f"""# {file_path}
# Generated from impact analysis requirements

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class {class_name}:
    \"\"\"Class for {file_name} functionality\"\"\"
    
    def __init__(self):
        self.initialized = True
        logger.info(f"{file_name} initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Process data according to requirements\"\"\"
        logger.info(f"Processing data in {file_name}")
        return {{"status": "processed", "data": data}}
"""
    
    def _generate_json_file_content(self, file_path: str, impact_content: str) -> str:
        """Generate JSON file content"""
        return """{
  "name": "backend-api",
  "version": "1.0.0",
  "description": "Generated from impact analysis requirements",
  "configuration": {
    "environment": "development",
    "debug": true
  }
}"""
    
    def _generate_yaml_file_content(self, file_path: str, impact_content: str) -> str:
        """Generate YAML file content"""
        if 'docker' in file_path.lower() or 'compose' in file_path.lower():
            return """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - ENVIRONMENT=development"""
        else:
            return """# Configuration file generated from impact analysis
name: backend-api
version: 1.0.0
environment: development
debug: true"""
    
    def _generate_markdown_content(self, file_path: str, impact_content: str) -> str:
        """Generate Markdown file content"""
        return f"""# {file_path.replace('.md', '').replace('_', ' ').title()}

Generated from impact analysis requirements.

## Overview

This document contains information about the {file_path.replace('.md', '')} component.

## Requirements

Based on the impact analysis document, this component should:

- Implement the specified functionality
- Follow the defined architecture
- Meet the performance requirements

## Usage

Refer to the main documentation for usage instructions.
"""
    
    def _generate_django_backend(self, project_spec: Dict[str, Any], project_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate comprehensive Django backend"""
        return {
            "requirements.txt": """Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
psycopg2-binary>=2.9.7
python-dotenv>=1.0.0
PyJWT>=2.8.0""",
            "manage.py": """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)""",
            "backend/settings.py": """import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}"""
        }
    
    def _generate_from_report_analysis(self, report_content: str, backend_stack: str, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend by analyzing report content with simpler approach"""
        self.logger.log("🔍 Analyzing report content for backend generation...")
        
        import re
        
        # Extract API endpoints from report
        endpoints = []
        endpoint_patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)',
            r'(GET|POST|PUT|DELETE|PATCH)\s*[:\-]?\s*(/[\w/{}:-]+)',
            r'endpoint[:\s]+(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)',
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, report_content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    method, path = match
                    endpoints.append({"method": method.upper(), "path": path})
        
        # Remove duplicates
        unique_endpoints = []
        seen = set()
        for ep in endpoints:
            key = f"{ep['method']}:{ep['path']}"
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(ep)
        
        self.logger.log(f"📍 Found {len(unique_endpoints)} API endpoints in report")
        for ep in unique_endpoints[:5]:
            self.logger.log(f"  - {ep['method']} {ep['path']}")
        
        # Extract data models
        models = []
        model_patterns = [
            r'(?:class|model|table)\s+(\w+)',
            r'(\w+)\s*(?:model|table|schema)',
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, report_content, re.IGNORECASE)
            models.extend(matches)
        
        # Clean up model names
        models = [m.title() for m in models if len(m) > 2 and m.lower() not in ['the', 'and', 'for', 'with']]
        models = list(set(models))[:5]  # Limit to 5 models
        
        self.logger.log(f"📊 Found {len(models)} data models: {', '.join(models)}")
        
        # Generate backend based on stack
        if "FastAPI" in backend_stack:
            return self._generate_fastapi_from_analysis(unique_endpoints, models, project_spec)
        elif "Django" in backend_stack:
            return self._generate_django_from_analysis(unique_endpoints, models, project_spec)
        else:
            return self._generate_fastapi_from_analysis(unique_endpoints, models, project_spec)
    
    def _generate_fastapi_from_analysis(self, endpoints: list, models: list, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate FastAPI backend from analyzed endpoints and models"""
        project_name = project_spec.get('overview', 'API').replace(' ', '_').lower()
        
        # Generate models
        models_code = """from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

"""
        
        for model in models:
            if model.lower() != 'user':
                models_code += f"""class {model}(Base):
    __tablename__ = "{model.lower()}s"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

"""
        
        # Generate routes
        routes_code = ""
        for ep in endpoints:
            method = ep['method']
            path = ep['path']
            func_name = path.replace('/', '_').replace('{', '').replace('}', '').strip('_')
            
            if method == 'GET':
                routes_code += f"""@app.get("{path}")
def {func_name}(db: Session = Depends(get_db)):
    return {{"message": "Endpoint {path}", "method": "{method}"}}

"""
            elif method == 'POST':
                routes_code += f"""@app.post("{path}")
def {func_name}(data: dict, db: Session = Depends(get_db)):
    return {{"message": "Created", "data": data}}

"""
            elif method in ['PUT', 'PATCH']:
                routes_code += f"""@app.{method.lower()}("{path}")
def {func_name}(data: dict, db: Session = Depends(get_db)):
    return {{"message": "Updated", "data": data}}

"""
            elif method == 'DELETE':
                routes_code += f"""@app.delete("{path}")
def {func_name}(db: Session = Depends(get_db)):
    return {{"message": "Deleted"}}

"""
        
        main_py = f"""from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base
import logging

Base.metadata.create_all(bind=engine)

app = FastAPI(title="{project_name.title()} API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {{"message": "API is running", "endpoints": {len(endpoints)}}}

@app.get("/health")
def health():
    return {{"status": "healthy"}}

{routes_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        return {
            "main.py": main_py,
            "models.py": models_code,
            "database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
            "requirements.txt": """fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
""",
            "README.md": f"""# {project_name.title()} API

Generated from Impact Analysis report.

## Endpoints

{chr(10).join(f'- {ep["method"]} {ep["path"]}' for ep in endpoints)}

## Setup

```bash
pip install -r requirements.txt
python main.py
```

API runs on http://localhost:8000
"""
        }
    
    def _generate_django_from_analysis(self, endpoints: list, models: list, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Django backend from analyzed endpoints and models"""
        return self._generate_fastapi_from_analysis(endpoints, models, project_spec)  # Fallback to FastAPI
    
    def _extract_api_specifications(self, content: str) -> Dict[str, Any]:
        """Extract API endpoints, models, and fields from Impact Analysis content"""
        import re
        
        specs = {
            "endpoints": [],
            "models": [],
            "fields": {},
            "requirements": []
        }
        
        # Extract API endpoints with various patterns
        endpoint_patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/api/[\w/{}:-]+)',
            r'(GET|POST|PUT|DELETE|PATCH)\s*[:\-]?\s*(/[\w/{}:-]+)',
            r'endpoint[:\s]+(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)',
            r'API[:\s]+(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)',
            r'route[:\s]+(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)',
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    method, path = match
                    endpoint = {
                        "method": method.upper(),
                        "path": path,
                        "description": f"{method.upper()} {path}"
                    }
                    if endpoint not in specs["endpoints"]:
                        specs["endpoints"].append(endpoint)
        
        # Extract data models/entities
        model_patterns = [
            r'(?:model|entity|table|class)\s+(\w+)',
            r'(\w+)\s*(?:model|entity|table|schema)',
            r'create\s+(\w+)\s*(?:model|table)',
            r'(\w+)\s*(?:has|contains|includes)\s*(?:fields|properties)',
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                model_name = match.title() if isinstance(match, str) else match[0].title()
                if len(model_name) > 2 and model_name not in ['The', 'And', 'For', 'With', 'Has', 'Contains']:
                    if model_name not in specs["models"]:
                        specs["models"].append(model_name)
        
        # Extract field specifications
        field_patterns = [
            r'(\w+)\s*[:\-]\s*(string|integer|boolean|date|email|text|number|float)',
            r'field[:\s]+(\w+)\s*[:\-]\s*(string|integer|boolean|date|email|text|number|float)',
            r'(\w+)\s*(?:field|property|attribute)\s*[:\-]\s*(string|integer|boolean|date|email|text|number|float)',
        ]
        
        for pattern in field_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    field_name, field_type = match
                    if 'fields' not in specs:
                        specs['fields'] = {}
                    specs['fields'][field_name] = field_type.lower()
        
        # Extract requirements
        requirement_patterns = [
            r'(?:requirement|must|should|need)[:\s]+([^\n\.]+)',
            r'(?:implement|create|build)[:\s]+([^\n\.]+)',
            r'(?:feature|functionality)[:\s]+([^\n\.]+)',
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                req = match.strip()
                if len(req) > 10 and req not in specs["requirements"]:
                    specs["requirements"].append(req)
        
        # Clean up and validate
        specs["endpoints"] = specs["endpoints"][:20]  # Limit to 20 endpoints
        specs["models"] = specs["models"][:10]  # Limit to 10 models
        specs["requirements"] = specs["requirements"][:10]  # Limit to 10 requirements
        
        return specs
    
    def _generate_from_extracted_specs(self, specs: Dict[str, Any], backend_stack: str, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend from extracted specifications"""
        self.logger.log(f"🔧 Generating {backend_stack} backend from extracted specifications...")
        
        endpoints = specs.get('endpoints', [])
        models = specs.get('models', [])
        fields = specs.get('fields', {})
        requirements = specs.get('requirements', [])
        
        self.logger.log(f"📊 Generating with: {len(endpoints)} endpoints, {len(models)} models, {len(fields)} fields")
        
        if "FastAPI" in backend_stack:
            return self._generate_fastapi_from_specs(endpoints, models, fields, requirements, project_spec)
        elif "Django" in backend_stack:
            return self._generate_django_from_specs(endpoints, models, fields, requirements, project_spec)
        else:
            return self._generate_fastapi_from_specs(endpoints, models, fields, requirements, project_spec)
    
    def _generate_fastapi_from_specs(self, endpoints: list, models: list, fields: dict, requirements: list, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate FastAPI backend from extracted specifications"""
        project_name = project_spec.get('overview', 'API').replace(' ', '_').lower()
        
        # Generate models with proper fields
        models_code = """from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

"""
        
        # Generate models based on specifications
        for model in models:
            if model.lower() != 'user':
                model_fields = []
                model_fields.append("    id = Column(Integer, primary_key=True, index=True)")
                
                # Add fields based on extracted field specifications
                for field_name, field_type in fields.items():
                    if field_type in ['string', 'text']:
                        model_fields.append(f"    {field_name} = Column(String, index=True)")
                    elif field_type in ['integer', 'number']:
                        model_fields.append(f"    {field_name} = Column(Integer)")
                    elif field_type == 'boolean':
                        model_fields.append(f"    {field_name} = Column(Boolean, default=False)")
                    elif field_type in ['date', 'datetime']:
                        model_fields.append(f"    {field_name} = Column(DateTime)")
                    elif field_type == 'float':
                        model_fields.append(f"    {field_name} = Column(Float)")
                    else:
                        model_fields.append(f"    {field_name} = Column(String)")
                
                # Add default fields if no specific fields found
                if not any(field_name in fields for field_name in ['name', 'title', 'description']):
                    model_fields.extend([
                        "    name = Column(String, index=True)",
                        "    description = Column(Text)"
                    ])
                
                model_fields.extend([
                    "    created_at = Column(DateTime, default=datetime.utcnow)",
                    "    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"
                ])
                
                models_code += f"""class {model}(Base):
    __tablename__ = "{model.lower()}s"
{chr(10).join(model_fields)}

"""
        
        # Generate schemas based on models and fields
        schemas_code = """from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

"""
        
        # Generate schemas for each model
        for model in models:
            if model.lower() != 'user':
                schema_fields = []
                for field_name, field_type in fields.items():
                    if field_type in ['string', 'text']:
                        schema_fields.append(f"    {field_name}: str")
                    elif field_type in ['integer', 'number']:
                        schema_fields.append(f"    {field_name}: int")
                    elif field_type == 'boolean':
                        schema_fields.append(f"    {field_name}: bool")
                    elif field_type in ['date', 'datetime']:
                        schema_fields.append(f"    {field_name}: datetime")
                    elif field_type == 'float':
                        schema_fields.append(f"    {field_name}: float")
                    else:
                        schema_fields.append(f"    {field_name}: str")
                
                if not schema_fields:
                    schema_fields = ["    name: str", "    description: Optional[str] = None"]
                
                schemas_code += f"""class {model}Base(BaseModel):
{chr(10).join(schema_fields)}

class {model}Create({model}Base):
    pass

class {model}Response({model}Base):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

"""
        
        # Generate routes based on extracted endpoints
        routes_code = ""
        for ep in endpoints:
            method = ep['method']
            path = ep['path']
            func_name = path.replace('/', '_').replace('{', '').replace('}', '').strip('_')
            
            if method == 'GET':
                if '{id}' in path or '{' in path:
                    routes_code += f"""@app.get("{path}")
def {func_name}(id: int, db: Session = Depends(get_db)):
    # Get single item by ID
    item = db.query(models.{models[0] if models else 'Item'}).filter(models.{models[0] if models else 'Item'}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

"""
                else:
                    routes_code += f"""@app.get("{path}")
def {func_name}(db: Session = Depends(get_db)):
    # Get all items
    items = db.query(models.{models[0] if models else 'Item'}).all()
    return {{"items": items, "total": len(items)}}

"""
            elif method == 'POST':
                model_name = models[0] if models else 'Item'
                routes_code += f"""@app.post("{path}")
def {func_name}(item_data: schemas.{model_name}Create, db: Session = Depends(get_db)):
    # Create new item
    new_item = models.{model_name}(**item_data.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

"""
            elif method in ['PUT', 'PATCH']:
                model_name = models[0] if models else 'Item'
                routes_code += f"""@app.{method.lower()}("{path}")
def {func_name}(id: int, item_data: schemas.{model_name}Create, db: Session = Depends(get_db)):
    # Update item
    item = db.query(models.{model_name}).filter(models.{model_name}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_data.dict().items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item

"""
            elif method == 'DELETE':
                model_name = models[0] if models else 'Item'
                routes_code += f"""@app.delete("{path}")
def {func_name}(id: int, db: Session = Depends(get_db)):
    # Delete item
    item = db.query(models.{model_name}).filter(models.{model_name}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {{"message": "Item deleted successfully"}}

"""
        
        # Generate main.py with all endpoints
        main_py = f"""from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db, engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{project_name.title()} API",
    description="Generated from Impact Analysis specifications",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {{
        "message": "API is running",
        "endpoints": {len(endpoints)},
        "models": {len(models)}
    }}

@app.get("/health")
def health():
    return {{"status": "healthy", "service": "{project_name}"}}

# Generated API endpoints
{routes_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        return {
            "main.py": main_py,
            "models.py": models_code,
            "schemas.py": schemas_code,
            "database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={{"check_same_thread": False}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
            "requirements.txt": """fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.7.4
python-dotenv>=1.0.0
""",
            "README.md": f"""# {project_name.title()} API

Generated from Impact Analysis specifications.

## Endpoints

{chr(10).join(f'- {ep["method"]} {ep["path"]}' for ep in endpoints)}

## Models

{chr(10).join(f'- {model}' for model in models)}

## Setup

```bash
pip install -r requirements.txt
python main.py
```

API runs on http://localhost:8000
Docs available at http://localhost:8000/docs
"""
        }
    
    def _generate_django_from_specs(self, endpoints: list, models: list, fields: dict, requirements: list, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Django backend from extracted specifications"""
        # For now, fallback to FastAPI
        return self._generate_fastapi_from_specs(endpoints, models, fields, requirements, project_spec)
    
    def _generate_nodejs_backend(self, project_spec: Dict[str, Any], project_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate comprehensive Node.js/Express backend"""
        return {
            "package.json": """{
  "name": "backend-api",
  "version": "1.0.0",
  "description": "Complete Node.js backend API",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "mongoose": "^7.5.0",
    "express-validator": "^7.0.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.7.0"
  }
}""",
            "server.js": """const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Backend API is running', status: 'success' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'backend-api' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});"""
        }