"""
IntegratorAgent - Combines everything, adds routing, env files, configs, tests, fixes errors
"""

from typing import Dict, Any
from pathlib import Path
import tempfile
import os
import json
from utils.logger import StreamlitLogger
from agents.frontend_integrator import FrontendIntegratorAgent
from agents.hardcode_remover import HardcodeRemoverAgent
from agents.auth_flow_fixer import AuthFlowFixerAgent

class IntegratorAgent:
    """Agent that integrates frontend and backend into a complete project"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
        self.frontend_integrator = FrontendIntegratorAgent(llm, logger)
        self.hardcode_remover = HardcodeRemoverAgent(llm, logger)
        self.auth_flow_fixer = AuthFlowFixerAgent(llm, logger)
    
    def integrate(
        self,
        project_config: Dict[str, Any],
        frontend_code: Dict[str, str],
        backend_code: Dict[str, str],
        project_spec: Dict[str, Any]
    ) -> str:
        """Original monolithic integrate method (maintained for backward compatibility)"""
        self.logger.log("🔗 Integrating frontend and backend...")
        
        # Handle None values for backward compatibility
        if frontend_code is None:
            frontend_code = {}
        if backend_code is None:
            backend_code = {}
        if project_spec is None:
            project_spec = {}

        try:
            project_path_str = self.assemble_project(project_config, frontend_code, backend_code)
            project_path = Path(project_path_str)
            
            if frontend_code:
                frontend_dir = project_path / "frontend"
                hardcode_analysis = self.run_hardcode_remover(frontend_dir, project_spec.get('api_endpoints', []))
                auth_results = self.run_auth_fixer(frontend_dir)
                self.run_api_integrator(frontend_dir, project_spec, backend_code)

                # Log comprehensive results
                self.logger.log(f"✅ Frontend transformation completed:")
                self.logger.log(f"  📁 Files processed: {hardcode_analysis['files_analyzed']}")
                self.logger.log(f"  ✏️ Files modified: {hardcode_analysis['files_modified']}")
                self.logger.log(f"  🔍 Hardcoded elements removed: {len(hardcode_analysis['hardcoded_elements_found'])}")
                self.logger.log(f"  🔄 Transformations applied: {len(hardcode_analysis['transformations_applied'])}")
                self.logger.log(f"  🔐 Auth issues fixed: {len(auth_results['auth_issues_fixed'])}")
                self.logger.log(f"  📄 New auth files created: {len(auth_results['new_files_created'])}")
                self.logger.log(f"  🛣️ Routing issues fixed: {len(auth_results['routing_issues_fixed'])}")
                
            self.finalize(project_path, project_config, project_spec)
            return project_path_str
        except Exception as e:
            self.logger.log(f"⚠️ Error during integration: {str(e)}", level="error")
            raise

    def assemble_project(
        self,
        project_config: Dict[str, Any],
        frontend_code: Dict[str, str],
        backend_code: Dict[str, str]
    ) -> str:
        """Step 1: Create directory structure and write base files"""
        self.logger.log("📁 Creating project structure and writing base files...")
        project_name = project_config["project_name"]
        temp_dir = tempfile.mkdtemp(prefix=f"{project_name}_")
        project_path = Path(temp_dir) / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Write frontend files
        if frontend_code:
            frontend_dir = project_path / "frontend"
            frontend_dir.mkdir(exist_ok=True)
            frontend_code = self._fix_frontend_packages(frontend_code)
            frontend_code = self._validate_html_files(frontend_code)
            self._write_files(frontend_dir, frontend_code)
            self.logger.log(f"✅ Wrote {len(frontend_code)} frontend files")

        # Write backend files
        if backend_code:
            backend_dir = project_path / "backend"
            backend_dir.mkdir(exist_ok=True)
            backend_code = self._fix_package_names(backend_code)
            self._write_files(backend_dir, backend_code)
            self.logger.log(f"✅ Wrote {len(backend_code)} backend files")
            
        return str(project_path)

    def run_hardcode_remover(self, frontend_dir: Path, endpoints: list) -> Dict[str, Any]:
        """Step 2: Remove hardcoded elements"""
        self.logger.log("🔧 Step 1: Removing hardcoded elements comprehensively...")
        results = self.hardcode_remover.analyze_and_remove_hardcode(frontend_dir, endpoints)
        return results

    def run_auth_fixer(self, frontend_dir: Path) -> Dict[str, Any]:
        """Step 3: Fix authentication flow"""
        self.logger.log("🔐 Step 2: Fixing authentication flow...")
        results = self.auth_flow_fixer.fix_authentication_flow(frontend_dir)
        return results

    def run_api_integrator(self, frontend_dir: Path, project_spec: Dict[str, Any], backend_code: Dict[str, str]):
        """Step 4: Integrate API calls"""
        self.logger.log("🔗 Step 3: Integrating API calls...")
        self._integrate_frontend_api(frontend_dir, project_spec, backend_code)

    def finalize(self, project_path: Path, project_config: Dict[str, Any], project_spec: Dict[str, Any]):
        """Step 5: Create root files and initialize git"""
        self.logger.log("⚙️ Finalizing project setup (root files, Docker, Git)...")
        self._create_root_files(project_path, project_config, project_spec)
        
        if self._needs_docker(project_config["backend_stack"]):
            self._create_docker_compose(project_path, project_config)
            
        self._init_git(project_path)
        self.logger.log("✅ Project integration completed")
    
    def _fix_package_names(self, files: Dict[str, str]) -> Dict[str, str]:
        """Fix common package name mistakes in requirements.txt"""
        fixed_files = files.copy()
        
        # Fix requirements.txt if it exists
        for file_path, content in fixed_files.items():
            if "requirements.txt" in file_path.lower() or file_path.endswith("requirements.txt"):
                fixed_content = content
                
                # First, ensure newlines are properly handled (unescape \n)
                fixed_content = self._unescape_content(fixed_content)
                
                # Fix dotenv -> python-dotenv (common mistake)
                import re
                # Replace dotenv==version with python-dotenv>=version
                fixed_content = re.sub(
                    r'^dotenv==([^\s]+)',
                    r'python-dotenv>=\1',
                    fixed_content,
                    flags=re.MULTILINE
                )
                # Replace dotenv>=version with python-dotenv>=version
                fixed_content = re.sub(
                    r'^dotenv>=([^\s]+)',
                    r'python-dotenv>=\1',
                    fixed_content,
                    flags=re.MULTILINE
                )
                # Replace standalone dotenv with python-dotenv (if not already python-dotenv)
                if "dotenv" in fixed_content and "python-dotenv" not in fixed_content:
                    fixed_content = re.sub(
                        r'^dotenv\s*$',
                        'python-dotenv>=1.0.0',
                        fixed_content,
                        flags=re.MULTILINE
                    )
                
                # Fix pydantic version - must be >=2.7.4 for langchain compatibility
                # Replace pydantic 1.x with pydantic 2.x
                fixed_content = re.sub(
                    r'^pydantic==1\.',
                    'pydantic>=2.7.4',
                    fixed_content,
                    flags=re.MULTILINE
                )
                fixed_content = re.sub(
                    r'^pydantic>=1\.',
                    'pydantic>=2.7.4',
                    fixed_content,
                    flags=re.MULTILINE
                )
                # If pydantic is specified but version is too old
                if re.search(r'^pydantic[<>=!]+.*1\.', fixed_content, re.MULTILINE):
                    fixed_content = re.sub(
                        r'^pydantic[<>=!]+.*1\.\d+',
                        'pydantic>=2.7.4',
                        fixed_content,
                        flags=re.MULTILINE
                    )
                    self.logger.log("🔧 Fixed pydantic version (1.x -> 2.7.4+) in requirements.txt")
                
                fixed_files[file_path] = fixed_content
                if fixed_content != content:
                    self.logger.log("🔧 Fixed package name/version in requirements.txt")
        
        return fixed_files
    
    def _fix_frontend_packages(self, files: Dict[str, str]) -> Dict[str, str]:
        """Fix common package version conflicts in package.json"""
        fixed_files = files.copy()
        
        # Fix package.json if it exists
        for file_path, content in fixed_files.items():
            if "package.json" in file_path.lower() and file_path.endswith("package.json"):
                fixed_content = self._unescape_content(content)
                
                # Fix Vite version conflicts
                import re
                import json
                
                try:
                    # Try to parse as JSON to fix version conflicts
                    pkg_data = json.loads(fixed_content)
                    
                    if "dependencies" in pkg_data or "devDependencies" in pkg_data:
                        deps = pkg_data.get("dependencies", {})
                        dev_deps = pkg_data.get("devDependencies", {})
                        
                        # Fix vite version if it's too old
                        if "vite" in deps:
                            vite_version = deps["vite"]
                            # If vite is version 2.x, upgrade to 5.x
                            if vite_version.startswith("^2.") or vite_version.startswith("2."):
                                deps["vite"] = "^5.0.0"
                                self.logger.log("🔧 Fixed vite version (2.x -> 5.x) in package.json")
                        
                        if "vite" in dev_deps:
                            vite_version = dev_deps["vite"]
                            if vite_version.startswith("^2.") or vite_version.startswith("2."):
                                dev_deps["vite"] = "^5.0.0"
                                self.logger.log("🔧 Fixed vite version (2.x -> 5.x) in package.json")
                        
                        # Ensure @vitejs/plugin-react is compatible with vite 5
                        if "@vitejs/plugin-react" in dev_deps and "vite" in (deps if "vite" in deps else dev_deps):
                            # Update plugin-react to version compatible with vite 5
                            dev_deps["@vitejs/plugin-react"] = "^4.0.0"
                            self.logger.log("🔧 Updated @vitejs/plugin-react to version 4.x for vite 5 compatibility")
                        
                        # Update package.json with fixed dependencies
                        pkg_data["dependencies"] = deps
                        pkg_data["devDependencies"] = dev_deps
                        fixed_content = json.dumps(pkg_data, indent=2)
                        
                except json.JSONDecodeError:
                    # If JSON parsing fails, try regex-based fixes
                    # Fix vite version in package.json string
                    fixed_content = re.sub(
                        r'"vite"\s*:\s*"[\^~]?2\.',
                        '"vite": "^5.',
                        fixed_content
                    )
                    if fixed_content != content:
                        self.logger.log("🔧 Fixed vite version using regex in package.json")
                
                fixed_files[file_path] = fixed_content
                if fixed_content != content:
                    self.logger.log("🔧 Fixed package version conflicts in package.json")
        
        return fixed_files
    
    def _unescape_content(self, content: str) -> str:
        """Unescape escape sequences in file content (e.g., \\n -> newline)"""
        # When JSON is parsed, \n should already be newlines, but sometimes
        # the LLM returns content with literal \n strings that need conversion
        # Simple approach: replace literal backslash-n with actual newline
        if '\\n' in content and content.count('\n') < content.count('\\n'):
            # More \n escape sequences than actual newlines, so unescape them
            content = content.replace('\\n', '\n')
            content = content.replace('\\t', '\t')
            content = content.replace('\\r', '\r')
        return content
    
    def _validate_html_files(self, files: Dict[str, str]) -> Dict[str, str]:
        """Validate and fix incomplete HTML files"""
        fixed_files = files.copy()
        
        for file_path, content in fixed_files.items():
            if file_path.endswith('.html') or file_path.endswith('.htm'):
                fixed_content = self._unescape_content(content)
                
                # Check if HTML is complete
                has_doctype = '<!DOCTYPE' in fixed_content or '<!doctype' in fixed_content
                has_html_open = '<html' in fixed_content
                has_html_close = '</html>' in fixed_content
                has_head_close = '</head>' in fixed_content
                has_body_open = '<body' in fixed_content
                has_body_close = '</body>' in fixed_content
                
                # If HTML appears incomplete, try to fix it
                if has_html_open and (not has_html_close or not has_body_close):
                    self.logger.log(f"⚠️ HTML file {file_path} appears incomplete, attempting to fix...")
                    
                    # Try to complete the HTML
                    if not has_doctype:
                        fixed_content = '<!DOCTYPE html>\n' + fixed_content
                    
                    if '<html' in fixed_content and '</html>' not in fixed_content:
                        # Add missing closing tags
                        if '<body' in fixed_content and '</body>' not in fixed_content:
                            # Add closing body tag
                            if '<div id="root">' in fixed_content or '<div id="app">' in fixed_content:
                                # React/Vue app - add script tag if missing
                                if '<script' not in fixed_content or 'src=' not in fixed_content:
                                    # Try to find the main entry point
                                    main_js = '/src/main.jsx' if 'main.jsx' in str(files.keys()) else '/src/main.js'
                                    fixed_content += f'\n    <script type="module" src="{main_js}"></script>'
                            fixed_content += '\n</body>'
                        
                        if '</head>' not in fixed_content and '<head' in fixed_content:
                            # Head tag not closed, try to close it
                            if '</head>' not in fixed_content:
                                # Find where head should close (before body)
                                if '<body' in fixed_content:
                                    fixed_content = fixed_content.replace('<body', '</head>\n<body', 1)
                                else:
                                    fixed_content += '\n</head>'
                        
                        fixed_content += '\n</html>'
                    
                    fixed_files[file_path] = fixed_content
                    self.logger.log(f"🔧 Fixed incomplete HTML file: {file_path}")
        
        return fixed_files
    
    def _write_files(self, base_dir: Path, files: Dict[str, str]):
        """Write files to directory structure"""
        for file_path, content in files.items():
            # Normalize path
            if file_path.startswith("/"):
                file_path = file_path[1:]
            
            full_path = base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Unescape content (handle \n -> newline, etc.)
            unescaped_content = self._unescape_content(content)
            
            # Write file
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(unescaped_content)
    
    def _create_root_files(self, project_path: Path, project_config: Dict[str, Any], project_spec: Dict[str, Any]):
        """Create root-level project files"""
        # README.md
        readme_content = f"""# {project_config['project_name']}

{project_config['description']}

## Tech Stack

- **Frontend**: {project_config['frontend_stack']}
- **Backend**: {project_config['backend_stack']}
- **Frontend Source**: GitHub ([Repository]({project_config.get('github_repo_url', '#')}))

## Project Structure

```
{project_config['project_name']}/
├── frontend/          # Frontend application
├── backend/           # Backend API
├── README.md          # This file
└── docker-compose.yml # Docker configuration (if applicable)
```

## Getting Started

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for Python backends)
- Docker (optional, for containerized setup)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Backend Setup

```bash
cd backend
# Follow backend-specific setup instructions in backend/README.md
```

## Features

{chr(10).join(f"- {feature}" for feature in project_spec.get('features', []))}

## API Endpoints

{chr(10).join(f"- `{ep.get('method', 'GET')} {ep.get('path', '/')}` - {ep.get('description', '')}" for ep in project_spec.get('api_endpoints', [])[:10])}

## License

MIT
"""
        
        with open(project_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # .gitignore
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# Build outputs
dist/
build/
*.egg-info/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
        
        with open(project_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
    
    def _needs_docker(self, backend_stack: str) -> bool:
        """Check if backend stack needs Docker"""
        return "FastAPI" in backend_stack or "Django" in backend_stack or "Node.js" in backend_stack
    
    def _create_docker_compose(self, project_path: Path, project_config: Dict[str, Any]):
        """Create docker-compose.yml file"""
        docker_content = """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
        
        with open(project_path / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(docker_content)
    
    def _integrate_frontend_api(self, frontend_dir: Path, project_spec: Dict[str, Any], backend_code: Dict[str, str]):
        """Integrate API calls into frontend components"""
        try:
            # Extract API endpoints from project spec
            endpoints = project_spec.get('api_endpoints', [])
            
            if not endpoints:
                # Generate default endpoints
                endpoints = [
                    {'method': 'GET', 'path': '/api/items', 'name': 'getItems'},
                    {'method': 'POST', 'path': '/api/items', 'name': 'createItem'},
                    {'method': 'PUT', 'path': '/api/items', 'name': 'updateItem'},
                    {'method': 'DELETE', 'path': '/api/items', 'name': 'deleteItem'},
                ]
            
            # Integrate API calls
            result = self.frontend_integrator.integrate_api_calls(
                frontend_dir,
                endpoints,
                backend_url="http://localhost:8000"
            )
            
            # Write API service file
            api_service_path = frontend_dir / "src" / "services"
            api_service_path.mkdir(parents=True, exist_ok=True)
            
            with open(api_service_path / "api.js", 'w', encoding='utf-8') as f:
                f.write(result['api_service'])
            
            self.logger.log("✅ Integrated API calls into frontend")
            
            # Create .env file for frontend
            env_content = """VITE_API_URL=http://localhost:8000
"""
            with open(frontend_dir / ".env", 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.logger.log("✅ Created frontend .env file")
            
            # Verify endpoints match
            self._verify_endpoints(frontend_dir, backend_code, endpoints)
            
        except Exception as e:
            self.logger.log(f"⚠️ Could not integrate API calls: {str(e)}", level="warning")
    
    def _verify_endpoints(self, frontend_dir: Path, backend_code: Dict[str, str], endpoints: list):
        """Verify that frontend and backend endpoints match"""
        try:
            import re
            
            # Extract backend endpoints from main.py
            backend_endpoints = []
            for file_path, content in backend_code.items():
                if 'main.py' in file_path:
                    # Find @app.get/post/put/delete patterns
                    patterns = [
                        r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for method, path in matches:
                            if '/auth/' not in path:  # Skip auth endpoints
                                backend_endpoints.append(f"{method.upper()} {path}")
            
            # Extract frontend endpoints from api.js
            api_js = frontend_dir / "src" / "services" / "api.js"
            frontend_endpoints = []
            
            if api_js.exists():
                with open(api_js, 'r', encoding='utf-8') as f:
                    content = f.read()
                    patterns = [
                        r'api\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for method, path in matches:
                            if '/auth/' not in path:
                                frontend_endpoints.append(f"{method.upper()} {path}")
            
            # Compare
            matching = set(backend_endpoints) & set(frontend_endpoints)
            
            if matching:
                self.logger.log(f"✅ Verified {len(matching)} matching endpoints between frontend and backend")
                for ep in sorted(matching):
                    self.logger.log(f"  ✓ {ep}")
            
            # Check for mismatches
            frontend_only = set(frontend_endpoints) - set(backend_endpoints)
            backend_only = set(backend_endpoints) - set(frontend_endpoints)
            
            if frontend_only:
                self.logger.log(f"⚠️ {len(frontend_only)} endpoints in frontend but not backend:", level="warning")
                for ep in sorted(frontend_only):
                    self.logger.log(f"  - {ep}", level="warning")
            
            if backend_only:
                self.logger.log(f"💡 {len(backend_only)} endpoints in backend not used by frontend:")
                for ep in sorted(backend_only):
                    self.logger.log(f"  + {ep}")
            
        except Exception as e:
            self.logger.log(f"⚠️ Could not verify endpoints: {str(e)}", level="warning")
    
    def _init_git(self, project_path: Path):
        """Initialize git repository"""
        try:
            import subprocess
            subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
            self.logger.log("✅ Initialized git repository")
        except Exception as e:
            self.logger.log(f"⚠️ Could not initialize git: {str(e)}", level="error")

