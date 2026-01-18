import os
try:
    import git
except ImportError:
    raise ImportError("GitPython is required. Install with: pip install gitpython")
import json
import re
import ast
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from app.core.utils import safe_remove_directory
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    method: str
    path: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    purpose: str
    dependencies: List[str]
    file_location: str
    line_number: int

@dataclass
class ComponentInfo:
    name: str
    type: str
    file_path: str
    dependencies: List[str]
    exports: List[str]
    props: Dict[str, Any]
    routes: List[str]

@dataclass
class RepositoryAnalysis:
    project_name: str
    description: str
    tech_stack: Dict[str, List[str]]
    frontend_structure: Dict[str, Any]
    backend_structure: Dict[str, Any]
    api_endpoints: List[APIEndpoint]
    components: List[ComponentInfo]
    database_schema: Dict[str, Any]
    build_tools: List[str]
    dependencies: Dict[str, List[str]]
    folder_structure: Dict[str, Any]
    business_logic: List[str]

class GitHubAnalyzerService:
    def __init__(self):
        self.supported_extensions = {
            'frontend': ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.html', '.css', '.scss', '.sass'],
            'backend': ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.env', '.config'],
            'database': ['.sql', '.prisma', '.graphql']
        }
        
        # Initialize Groq service if API key is available
        self.groq_service = None
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            try:
                from app.services.groq_service import GroqService
                self.groq_service = GroqService(groq_api_key)
                logger.info("Groq LLM service initialized for enhanced analysis")
            except Exception as e:
                logger.warning(f"Could not initialize Groq service: {str(e)}")
                self.groq_service = None
        
    def clone_repository(self, github_url: str, github_token: Optional[str] = None) -> str:
        """Clone GitHub repository to temporary directory"""
        try:
            temp_dir = tempfile.mkdtemp()
            
            # Add token to URL if provided
            if github_token and 'github.com' in github_url:
                # Convert https://github.com/user/repo to https://token@github.com/user/repo
                if github_url.startswith('https://github.com/'):
                    github_url = github_url.replace('https://github.com/', f'https://{github_token}@github.com/')
            
            logger.info(f"Cloning repository to {temp_dir}")
            git.Repo.clone_from(github_url, temp_dir)
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise Exception(f"Repository cloning failed: {str(e)}")
    
    def analyze_repository(self, github_url: str, github_token: Optional[str] = None) -> RepositoryAnalysis:
        """Comprehensive repository analysis"""
        repo_path = None
        try:
            # Clone repository
            repo_path = self.clone_repository(github_url, github_token)
            
            # Extract project info
            project_name = self._extract_project_name(repo_path)
            description = self._extract_description(repo_path)
            
            # Analyze folder structure
            folder_structure = self._analyze_folder_structure(repo_path)
            
            # Detect tech stack
            tech_stack = self._detect_tech_stack(repo_path)
            
            # Analyze frontend structure
            frontend_structure = self._analyze_frontend_structure(repo_path)
            
            # Analyze backend structure
            backend_structure = self._analyze_backend_structure(repo_path)
            
            # Extract API endpoints
            api_endpoints = self._extract_api_endpoints(repo_path)
            
            # Analyze components
            components = self._analyze_components(repo_path)
            
            # Analyze database schema
            database_schema = self._analyze_database_schema(repo_path)
            
            # Detect build tools
            build_tools = self._detect_build_tools(repo_path)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(repo_path)
            
            # Extract business logic
            business_logic = self._extract_business_logic(repo_path)
            
            # Create initial analysis
            repo_analysis = RepositoryAnalysis(
                project_name=project_name,
                description=description,
                tech_stack=tech_stack,
                frontend_structure=frontend_structure,
                backend_structure=backend_structure,
                api_endpoints=api_endpoints,
                components=components,
                database_schema=database_schema,
                build_tools=build_tools,
                dependencies=dependencies,
                folder_structure=folder_structure,
                business_logic=business_logic
            )
            
            # Enhance with LLM analysis if available
            if self.groq_service:
                logger.info("Enhancing analysis with Groq LLM...")
                repo_analysis = self._enhance_analysis_with_llm(repo_analysis, repo_path)
            
            return repo_analysis
            
        finally:
            # Cleanup temporary directory
            if repo_path:
                safe_remove_directory(repo_path)
    
    def _extract_project_name(self, repo_path: str) -> str:
        """Extract project name from package.json, setup.py, or directory name"""
        # Try package.json
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('name', os.path.basename(repo_path))
            except:
                pass
        
        # Try setup.py
        setup_py = os.path.join(repo_path, 'setup.py')
        if os.path.exists(setup_py):
            try:
                with open(setup_py, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except:
                pass
        
        return os.path.basename(repo_path)
    
    def _extract_description(self, repo_path: str) -> str:
        """Extract project description from README or package.json"""
        # Try README files
        for readme_name in ['README.md', 'README.rst', 'README.txt', 'readme.md']:
            readme_path = os.path.join(repo_path, readme_name)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract first paragraph or first 200 chars
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#') and len(line) > 20:
                                return line[:200]
                except:
                    pass
        
        # Try package.json description
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('description', 'No description available')
            except:
                pass
        
        return 'No description available'
    
    def _analyze_folder_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze and map folder structure"""
        structure = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist', 'target']]
            
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = 'root'
            
            structure[rel_path] = {
                'directories': dirs,
                'files': files,
                'file_count': len(files),
                'file_types': list(set([os.path.splitext(f)[1] for f in files if os.path.splitext(f)[1]]))
            }
        
        return structure
    
    def _detect_tech_stack(self, repo_path: str) -> Dict[str, List[str]]:
        """Detect technology stack from files and dependencies"""
        tech_stack = {
            'frontend': [],
            'backend': [],
            'database': [],
            'tools': [],
            'languages': []
        }
        
        # Check for specific files and patterns
        files_to_check = {
            'package.json': 'frontend',
            'requirements.txt': 'backend',
            'Pipfile': 'backend',
            'pom.xml': 'backend',
            'go.mod': 'backend',
            'Gemfile': 'backend',
            'composer.json': 'backend',
            'Dockerfile': 'tools',
            'docker-compose.yml': 'tools',
            '.github/workflows': 'tools'
        }
        
        for file_pattern, category in files_to_check.items():
            if os.path.exists(os.path.join(repo_path, file_pattern)):
                if file_pattern == 'package.json':
                    tech_stack['frontend'].extend(self._analyze_package_json(repo_path))
                elif file_pattern == 'requirements.txt':
                    tech_stack['backend'].extend(self._analyze_requirements_txt(repo_path))
        
        # Detect languages by file extensions
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext == '.py':
                    tech_stack['languages'].append('Python')
                elif ext in ['.js', '.jsx']:
                    tech_stack['languages'].append('JavaScript')
                elif ext in ['.ts', '.tsx']:
                    tech_stack['languages'].append('TypeScript')
                elif ext == '.java':
                    tech_stack['languages'].append('Java')
                elif ext == '.go':
                    tech_stack['languages'].append('Go')
                elif ext == '.rb':
                    tech_stack['languages'].append('Ruby')
                elif ext == '.php':
                    tech_stack['languages'].append('PHP')
        
        # Remove duplicates
        for key in tech_stack:
            tech_stack[key] = list(set(tech_stack[key]))
        
        return tech_stack
    
    def _analyze_package_json(self, repo_path: str) -> List[str]:
        """Analyze package.json for frontend technologies"""
        technologies = []
        package_json_path = os.path.join(repo_path, 'package.json')
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                # Common frontend frameworks and libraries
                framework_mapping = {
                    'react': 'React',
                    'vue': 'Vue.js',
                    'angular': 'Angular',
                    'svelte': 'Svelte',
                    'next': 'Next.js',
                    'nuxt': 'Nuxt.js',
                    'gatsby': 'Gatsby',
                    'express': 'Express.js',
                    'fastify': 'Fastify',
                    'koa': 'Koa.js',
                    'webpack': 'Webpack',
                    'vite': 'Vite',
                    'parcel': 'Parcel'
                }
                
                for dep in deps:
                    for key, tech in framework_mapping.items():
                        if key in dep.lower():
                            technologies.append(tech)
                            break
        except:
            pass
        
        return technologies
    
    def _analyze_requirements_txt(self, repo_path: str) -> List[str]:
        """Analyze requirements.txt for backend technologies"""
        technologies = []
        req_path = os.path.join(repo_path, 'requirements.txt')
        
        try:
            with open(req_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                framework_mapping = {
                    'django': 'Django',
                    'flask': 'Flask',
                    'fastapi': 'FastAPI',
                    'tornado': 'Tornado',
                    'pyramid': 'Pyramid',
                    'sqlalchemy': 'SQLAlchemy',
                    'celery': 'Celery',
                    'redis': 'Redis',
                    'postgresql': 'PostgreSQL',
                    'mysql': 'MySQL'
                }
                
                for framework, tech in framework_mapping.items():
                    if framework in content.lower():
                        technologies.append(tech)
        except:
            pass
        
        return technologies
    
    def _analyze_frontend_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze frontend structure - pages, components, routes"""
        structure = {
            'pages': [],
            'components': [],
            'routes': [],
            'state_management': [],
            'styling': []
        }
        
        # Common frontend directories
        frontend_dirs = ['src', 'app', 'pages', 'components', 'views', 'screens']
        
        for root, dirs, files in os.walk(repo_path):
            rel_path = os.path.relpath(root, repo_path)
            
            # Skip node_modules and other build directories
            if 'node_modules' in rel_path or '__pycache__' in rel_path:
                continue
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']):
                    file_path = os.path.join(root, file)
                    
                    # Categorize files
                    if 'page' in file.lower() or 'pages' in rel_path.lower():
                        structure['pages'].append({
                            'name': file,
                            'path': rel_path,
                            'routes': self._extract_routes_from_file(file_path)
                        })
                    elif 'component' in file.lower() or 'components' in rel_path.lower():
                        structure['components'].append({
                            'name': file,
                            'path': rel_path,
                            'props': self._extract_props_from_file(file_path)
                        })
        
        return structure
    
    def _analyze_backend_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze backend structure - services, models, controllers"""
        structure = {
            'services': [],
            'models': [],
            'controllers': [],
            'routers': [],
            'middleware': [],
            'utils': []
        }
        
        for root, dirs, files in os.walk(repo_path):
            rel_path = os.path.relpath(root, repo_path)
            
            # Skip build directories
            if any(skip in rel_path for skip in ['node_modules', '__pycache__', '.git']):
                continue
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.go']):
                    file_path = os.path.join(root, file)
                    
                    # Categorize backend files
                    if any(keyword in file.lower() for keyword in ['service', 'services']):
                        structure['services'].append({
                            'name': file,
                            'path': rel_path,
                            'functions': self._extract_functions_from_file(file_path)
                        })
                    elif any(keyword in file.lower() for keyword in ['model', 'models', 'schema']):
                        structure['models'].append({
                            'name': file,
                            'path': rel_path,
                            'classes': self._extract_classes_from_file(file_path)
                        })
                    elif any(keyword in file.lower() for keyword in ['controller', 'controllers', 'router', 'routes']):
                        structure['controllers'].append({
                            'name': file,
                            'path': rel_path,
                            'endpoints': self._extract_endpoints_from_file(file_path)
                        })
        
        return structure
    
    def _extract_api_endpoints(self, repo_path: str) -> List[APIEndpoint]:
        """Extract all API endpoints from the codebase with enhanced detection"""
        endpoints = []
        
        # Priority files to check first (more likely to contain endpoints)
        priority_patterns = ['main.py', 'app.py', 'server.py', 'index.js', 'server.js', 'routes.py', 'urls.py', 'api.py']
        
        for root, dirs, files in os.walk(repo_path):
            # Skip build directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'build', 'dist', 'venv', 'env']]
            
            # Sort files to prioritize likely endpoint files
            sorted_files = sorted(files, key=lambda f: (
                0 if any(pattern in f.lower() for pattern in priority_patterns) else 1,
                0 if any(keyword in f.lower() for keyword in ['route', 'api', 'endpoint', 'controller']) else 1,
                f
            ))
            
            for file in sorted_files:
                if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php']):
                    file_path = os.path.join(root, file)
                    file_endpoints = self._extract_endpoints_from_file(file_path)
                    
                    for endpoint_data in file_endpoints:
                        # Skip duplicate endpoints
                        existing_paths = [ep.path for ep in endpoints]
                        if endpoint_data.get('path') not in existing_paths:
                            endpoint = APIEndpoint(
                                method=endpoint_data.get('method', 'GET'),
                                path=endpoint_data.get('path', ''),
                                input_schema=endpoint_data.get('input_schema', {}),
                                output_schema=endpoint_data.get('output_schema', {}),
                                purpose=endpoint_data.get('purpose', ''),
                                dependencies=endpoint_data.get('dependencies', []),
                                file_location=os.path.relpath(file_path, repo_path),
                                line_number=endpoint_data.get('line_number', 0)
                            )
                            endpoints.append(endpoint)
        
        # If still no endpoints found, do a more aggressive search
        if len(endpoints) == 0:
            endpoints = self._aggressive_endpoint_search(repo_path)
        
        return endpoints
    
    def _aggressive_endpoint_search(self, repo_path: str) -> List[APIEndpoint]:
        """More aggressive search for API endpoints when initial search fails"""
        endpoints = []
        
        # Search for any file that might contain API definitions
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'build', 'dist']]
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.json', '.yaml', '.yml']):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Look for OpenAPI/Swagger definitions
                            if file.endswith(('.json', '.yaml', '.yml')):
                                if 'paths:' in content or '"paths"' in content:
                                    swagger_endpoints = self._extract_swagger_endpoints(content, file_path, repo_path)
                                    endpoints.extend(swagger_endpoints)
                            
                            # Look for any HTTP method mentions with paths
                            http_patterns = [
                                r'(GET|POST|PUT|DELETE|PATCH)\s+["\']?(/[^\s"\'\r?]+)["\']?',
                                r'["\']?(GET|POST|PUT|DELETE|PATCH)["\']?\s*[:=]\s*["\']?(/[^\s"\'\r]+)["\']?',
                            ]
                            
                            for pattern in http_patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    method = match.group(1).upper()
                                    path = match.group(2)
                                    if len(path) > 1 and path.startswith('/'):
                                        endpoints.append(APIEndpoint(
                                            method=method,
                                            path=path,
                                            input_schema={},
                                            output_schema={},
                                            purpose=f'HTTP method pattern found in {os.path.basename(file_path)}',
                                            dependencies=[],
                                            file_location=os.path.relpath(file_path, repo_path),
                                            line_number=0
                                        ))
                    except:
                        continue
        
        return endpoints[:10]  # Limit to top 10 to avoid noise
    
    def _extract_swagger_endpoints(self, content: str, file_path: str, repo_path: str) -> List[APIEndpoint]:
        """Extract endpoints from Swagger/OpenAPI definitions"""
        endpoints = []
        
        try:
            if file_path.endswith('.json'):
                import json
                data = json.loads(content)
            else:
                # Simple YAML parsing for paths
                lines = content.split('\n')
                paths_section = False
                current_path = None
                
                for line in lines:
                    if 'paths:' in line:
                        paths_section = True
                        continue
                    
                    if paths_section:
                        if line.strip().startswith('/'):
                            current_path = line.strip().rstrip(':')
                        elif current_path and any(method in line.lower() for method in ['get:', 'post:', 'put:', 'delete:', 'patch:']):
                            method = line.strip().rstrip(':').upper()
                            endpoints.append(APIEndpoint(
                                method=method,
                                path=current_path,
                                input_schema={},
                                output_schema={},
                                purpose=f'Swagger/OpenAPI endpoint from {os.path.basename(file_path)}',
                                dependencies=[],
                                file_location=os.path.relpath(file_path, repo_path),
                                line_number=0
                            ))
        except:
            pass
        
        return endpoints
    
    def _extract_endpoints_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from a single file with enhanced detection"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Enhanced patterns for different frameworks
                patterns = [
                    # FastAPI/Flask patterns
                    r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    r'@bp\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',  # Flask blueprints
                    # Express.js patterns
                    r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    # Django patterns
                    r'path\(["\']([^"\']+)["\'].*views\.(\w+)',
                    r'url\(["\']([^"\']+)["\'].*views\.(\w+)',
                    # Spring Boot patterns
                    r'@(Get|Post|Put|Delete|Patch)Mapping\(["\']([^"\']+)["\']',
                    # ASP.NET patterns
                    r'\[(Http(Get|Post|Put|Delete|Patch))\(["\']([^"\']+)["\']',
                    # Additional patterns for better detection
                    r'@(get|post|put|delete|patch)\(["\']([^"\']+)["\']',  # Lowercase decorators
                    r'Route\(["\']([^"\']+)["\'].*\[(Get|Post|Put|Delete|Patch)\]',  # ASP.NET Core
                    r'fetch\(["\']([^"\']+)["\']',  # Frontend fetch calls
                    r'axios\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',  # Axios calls
                    r'\$http\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',  # AngularJS
                ]
                
                # Also look for function definitions that might be endpoints
                function_patterns = [
                    r'def\s+(\w*api\w*|\w*endpoint\w*|\w*route\w*|\w*handler\w*)\s*\(',  # Python
                    r'function\s+(\w*api\w*|\w*endpoint\w*|\w*route\w*|\w*handler\w*)\s*\(',  # JavaScript
                    r'async\s+def\s+(\w+)\s*\(',  # Python async functions (likely FastAPI)
                    r'const\s+(\w*api\w*|\w*endpoint\w*|\w*route\w*|\w*handler\w*)\s*=',  # JS const functions
                    # r'export\s+(?:async\s+)?function\s+(\w+)',  # Removed: Too aggressive, matches frontend utils
                ]
                
                for i, line in enumerate(lines):
                    # Check explicit endpoint patterns
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            if len(match.groups()) >= 2:
                                if 'mapping' in pattern.lower() or 'http' in pattern.lower():
                                    # Spring Boot or ASP.NET
                                    method = match.group(1).replace('Mapping', '').replace('Http', '').upper()
                                    path = match.group(2) if len(match.groups()) > 2 else match.group(1)
                                else:
                                    method = match.group(1).upper()
                                    path = match.group(2) if '/' in match.group(2) else match.group(1)
                                
                                endpoints.append({
                                    'method': method,
                                    'path': path,
                                    'line_number': i + 1,
                                    'purpose': self._extract_function_purpose(lines, i),
                                    'input_schema': {},
                                    'output_schema': {},
                                    'dependencies': []
                                })
                    
                    # Check for potential API functions
                    for pattern in function_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            function_name = match.group(1) if len(match.groups()) >= 1 else 'api_function'
                            endpoints.append({
                                'method': 'GET',  # Default method
                                'path': f'/api/{function_name.lower()}',
                                'line_number': i + 1,
                                'purpose': f'Potential API function: {function_name}',
                                'input_schema': {},
                                'output_schema': {},
                                'dependencies': []
                            })
                
                # Look for URL patterns in comments or strings
                url_patterns = [
                    r'["\'](/api/[^"\'\r?]+)["\']',  # API URLs in strings
                    r'["\'](/[^"\'\r]*(?:users?|auth|login|register|data|items?|products?)[^"\'\r?]*)["\']',  # Common endpoint patterns
                    r'#\s*(/api/[^\n]+)',  # API URLs in comments
                ]
                
                for pattern in url_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        path = match.group(1)
                        if len(path) > 3 and not any(skip in path.lower() for skip in ['test', 'example', 'sample']):
                            endpoints.append({
                                'method': 'GET',  # Default method
                                'path': path,
                                'line_number': 0,
                                'purpose': f'URL pattern found in code: {path}',
                                'input_schema': {},
                                'output_schema': {},
                                'dependencies': []
                            })
                
                # Only create estimated endpoints if this is clearly a web framework file and no real endpoints found
                if not endpoints and any(framework in content.lower() for framework in ['flask', 'django', 'express', 'fastapi', 'spring', 'asp.net']):
                    # More conservative estimation
                    function_count = len(re.findall(r'def\s+\w+|function\s+\w+|async\s+def', content))
                    
                    # Only estimate if there are actual functions that could be endpoints
                    if function_count > 2:
                        estimated_endpoints = min(function_count // 2, 5)  # More conservative
                        for i in range(estimated_endpoints):
                            endpoints.append({
                                'method': 'GET',
                                'path': f'/api/function_{i+1}',
                                'line_number': 0,
                                'purpose': f'Estimated from {function_count} functions in {os.path.basename(file_path)}',
                                'input_schema': {},
                                'output_schema': {},
                                'dependencies': []
                            })
                        
        except Exception as e:
            logger.warning(f"Could not parse file {file_path}: {str(e)}")
        
        return endpoints
    
    def _extract_functions_from_file(self, file_path: str) -> List[str]:
        """Extract function names from a file"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if file_path.endswith('.py'):
                    # Python function pattern
                    pattern = r'def\s+(\w+)\s*\('
                elif file_path.endswith(('.js', '.ts')):
                    # JavaScript/TypeScript function patterns
                    pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=|(\w+)\s*:\s*function)'
                else:
                    return functions
                
                matches = re.finditer(pattern, content)
                for match in matches:
                    func_name = next(group for group in match.groups() if group)
                    if func_name:
                        functions.append(func_name)
        except:
            pass
        
        return functions
    
    def _extract_classes_from_file(self, file_path: str) -> List[str]:
        """Extract class names from a file"""
        classes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if file_path.endswith('.py'):
                    pattern = r'class\s+(\w+)'
                elif file_path.endswith(('.js', '.ts')):
                    pattern = r'class\s+(\w+)'
                else:
                    return classes
                
                matches = re.finditer(pattern, content)
                for match in matches:
                    classes.append(match.group(1))
        except:
            pass
        
        return classes
    
    def _extract_routes_from_file(self, file_path: str) -> List[str]:
        """Extract routes from frontend files"""
        routes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # React Router patterns
                route_patterns = [
                    r'<Route\s+path=["\']([^"\']+)["\']',
                    r'path:\s*["\']([^"\']+)["\']',
                    r'route\(["\']([^"\']+)["\']'
                ]
                
                for pattern in route_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        routes.append(match.group(1))
        except:
            pass
        
        return routes
    
    def _extract_props_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract component props from frontend files"""
        props = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # React props pattern
                props_pattern = r'(?:interface|type)\s+\w*Props\s*=?\s*{([^}]+)}'
                match = re.search(props_pattern, content, re.DOTALL)
                
                if match:
                    props_content = match.group(1)
                    prop_lines = props_content.split('\n')
                    
                    for line in prop_lines:
                        line = line.strip()
                        if ':' in line:
                            prop_match = re.match(r'(\w+)\??\s*:\s*([^;,]+)', line)
                            if prop_match:
                                props[prop_match.group(1)] = prop_match.group(2).strip()
        except:
            pass
        
        return props
    
    def _analyze_components(self, repo_path: str) -> List[ComponentInfo]:
        """Analyze all components in the repository"""
        components = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git']]
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']):
                    file_path = os.path.join(root, file)
                    
                    component = ComponentInfo(
                        name=os.path.splitext(file)[0],
                        type=self._determine_component_type(file_path),
                        file_path=os.path.relpath(file_path, repo_path),
                        dependencies=self._extract_imports_from_file(file_path),
                        exports=self._extract_exports_from_file(file_path),
                        props=self._extract_props_from_file(file_path),
                        routes=self._extract_routes_from_file(file_path)
                    )
                    components.append(component)
        
        return components
    
    def _determine_component_type(self, file_path: str) -> str:
        """Determine the type of component based on file content and location"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if 'useState' in content or 'useEffect' in content:
                    return 'React Component'
                elif 'Vue.component' in content or '<template>' in content:
                    return 'Vue Component'
                elif 'export default' in content and 'function' in content:
                    return 'Function Component'
                elif 'class' in content and 'extends' in content:
                    return 'Class Component'
                else:
                    return 'Module'
        except:
            return 'Unknown'
    
    def _extract_imports_from_file(self, file_path: str) -> List[str]:
        """Extract import statements from a file"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # JavaScript/TypeScript import patterns
                import_patterns = [
                    r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
                    r'import\s+["\']([^"\']+)["\']',
                    r'require\(["\']([^"\']+)["\']\)'
                ]
                
                for pattern in import_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        imports.append(match.group(1))
        except:
            pass
        
        return imports
    
    def _extract_exports_from_file(self, file_path: str) -> List[str]:
        """Extract export statements from a file"""
        exports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                export_patterns = [
                    r'export\s+(?:default\s+)?(?:function\s+)?(\w+)',
                    r'export\s+{\s*([^}]+)\s*}',
                    r'module\.exports\s*=\s*(\w+)'
                ]
                
                for pattern in export_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        export_item = match.group(1)
                        if ',' in export_item:
                            exports.extend([item.strip() for item in export_item.split(',')])
                        else:
                            exports.append(export_item)
        except:
            pass
        
        return exports
    
    def _analyze_database_schema(self, repo_path: str) -> Dict[str, Any]:
        """Analyze database schema from migration files, models, or SQL files"""
        schema = {
            'tables': [],
            'relationships': [],
            'indexes': []
        }
        
        # Look for database-related files
        db_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if any(file.endswith(ext) for ext in ['.sql', '.prisma']) or 'migration' in file.lower():
                    db_files.append(os.path.join(root, file))
        
        for file_path in db_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Extract table definitions
                    table_patterns = [
                        r'CREATE TABLE\s+(\w+)',
                        r'model\s+(\w+)\s*{',  # Prisma
                        r'class\s+(\w+)\(.*Model\)'  # Django/SQLAlchemy
                    ]
                    
                    for pattern in table_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            table_name = match.group(1)
                            if table_name not in [t['name'] for t in schema['tables']]:
                                schema['tables'].append({
                                    'name': table_name,
                                    'file': os.path.relpath(file_path, repo_path)
                                })
            except:
                pass
        
        return schema
    
    def _detect_build_tools(self, repo_path: str) -> List[str]:
        """Detect build tools and CI/CD configurations"""
        build_tools = []
        
        build_files = {
            'package.json': 'npm/yarn',
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite',
            'rollup.config.js': 'Rollup',
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose',
            'Makefile': 'Make',
            'setup.py': 'Python setuptools',
            'pyproject.toml': 'Python Poetry/setuptools',
            'pom.xml': 'Maven',
            'build.gradle': 'Gradle',
            'go.mod': 'Go Modules'
        }
        
        for file_name, tool in build_files.items():
            if os.path.exists(os.path.join(repo_path, file_name)):
                build_tools.append(tool)
        
        # Check for CI/CD
        ci_paths = [
            '.github/workflows',
            '.gitlab-ci.yml',
            'Jenkinsfile',
            '.travis.yml',
            'circle.yml'
        ]
        
        for ci_path in ci_paths:
            if os.path.exists(os.path.join(repo_path, ci_path)):
                build_tools.append('CI/CD')
                break
        
        return build_tools
    
    def _extract_dependencies(self, repo_path: str) -> Dict[str, List[str]]:
        """Extract project dependencies"""
        dependencies = {
            'production': [],
            'development': [],
            'python': [],
            'javascript': []
        }
        
        # JavaScript dependencies
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    dependencies['production'].extend(list(data.get('dependencies', {}).keys()))
                    dependencies['development'].extend(list(data.get('devDependencies', {}).keys()))
                    dependencies['javascript'] = dependencies['production'] + dependencies['development']
            except:
                pass
        
        # Python dependencies
        requirements_txt = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(requirements_txt):
            try:
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    deps = [line.split('==')[0].split('>=')[0].strip() for line in f.readlines() if line.strip()]
                    dependencies['python'].extend(deps)
            except:
                pass
        
        return dependencies
    
    def _extract_business_logic(self, repo_path: str) -> List[str]:
        """Extract business logic patterns and key functionality"""
        business_logic = []
        
        # Look for common business logic patterns
        patterns = [
            'authentication',
            'authorization',
            'payment',
            'user management',
            'data validation',
            'email sending',
            'file upload',
            'search functionality',
            'caching',
            'logging',
            'error handling'
        ]
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git']]
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.py', '.js', '.ts']):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            for pattern in patterns:
                                if pattern.replace(' ', '') in content or pattern in content:
                                    if pattern not in business_logic:
                                        business_logic.append(pattern)
                    except:
                        pass
        
        return business_logic
    
    def _extract_function_purpose(self, lines: List[str], line_index: int) -> str:
        """Extract function purpose from docstring or comments"""
        purpose = ""
        
        # Look for docstring or comments near the function
        for i in range(max(0, line_index - 2), min(len(lines), line_index + 5)):
            line = lines[i].strip()
            if '"""' in line or "'''" in line or line.startswith('#') or line.startswith('//'):
                # Extract meaningful text
                clean_line = re.sub(r'["""\'#/\*]', '', line).strip()
                if len(clean_line) > 10:
                    purpose = clean_line[:100]
                    break
        
        return purpose
    
    def _enhance_analysis_with_llm(self, repo_analysis: 'RepositoryAnalysis', repo_path: str) -> 'RepositoryAnalysis':
        """Enhance repository analysis using Groq LLM"""
        if not self.groq_service:
            return repo_analysis
        
        try:
            # Prepare context for LLM analysis
            analysis_context = {
                'project_name': repo_analysis.project_name,
                'description': repo_analysis.description,
                'languages': repo_analysis.tech_stack.get('languages', []),
                'file_count': sum(len(folder_info.get('files', [])) for folder_info in repo_analysis.folder_structure.values() if isinstance(folder_info, dict)),
                'folder_structure': list(repo_analysis.folder_structure.keys())[:10],  # Top 10 folders
                'dependencies': {
                    'production': repo_analysis.dependencies.get('production', [])[:10],
                    'development': repo_analysis.dependencies.get('development', [])[:5]
                },
                'build_tools': repo_analysis.build_tools,
                'business_logic': repo_analysis.business_logic[:5]  # Top 5 business logic items
            }
            
            # Create LLM prompt for enhanced analysis
            prompt = f"""
            Analyze this GitHub repository and provide enhanced insights:
            
            Project: {analysis_context['project_name']}
            Description: {analysis_context['description']}
            Languages: {', '.join(analysis_context['languages'])}
            File Count: {analysis_context['file_count']}
            Key Folders: {', '.join(analysis_context['folder_structure'])}
            Build Tools: {', '.join(analysis_context['build_tools'])}
            
            Based on this information, provide:
            1. Estimated API endpoints (if this is a web application)
            2. Estimated number of components (if this has a frontend)
            3. Estimated number of services (if this has a backend)
            4. Application type classification
            5. Architecture pattern
            
            Respond in JSON format:
            {{
                "estimated_api_endpoints": <number>,
                "estimated_components": <number>, 
                "estimated_services": <number>,
                "application_type": "<type>",
                "architecture_pattern": "<pattern>",
                "confidence_score": <0-100>
            }}
            """
            
            # Get LLM analysis
            llm_response = self.groq_service._generate_completion(prompt)
            
            if llm_response:
                # Try to parse JSON response using robust extraction
                try:
                    import json
                    content = llm_response.strip()
                    
                    # Robust extraction method matches what PlannerAgent uses
                    # Method 1: Extract from markdown code blocks
                    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)
                    else:
                        # Method 2: Find JSON object directly (greedy match)
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            content = json_match.group(0)
                    
                    llm_analysis = json.loads(content)
                    
                    # Update repository analysis with LLM insights
                    if llm_analysis.get('confidence_score', 0) > 70:  # Only use if confidence is high
                        # Don't create generic endpoints - let the architecture service handle this
                        pass
                        
                        # Create enhanced components if estimated
                        estimated_components = llm_analysis.get('estimated_components', 0)
                        if estimated_components > 0 and len(repo_analysis.components) == 0:
                            for i in range(min(estimated_components, 15)):  # Max 15 estimated components
                                component = ComponentInfo(
                                    name=f'Component_{i+1}',
                                    type='Estimated Component',
                                    file_path='estimated',
                                    dependencies=[],
                                    exports=[],
                                    props={},
                                    routes=[]
                                )
                                repo_analysis.components.append(component)
                        
                        logger.info(f"LLM enhanced analysis: endpoints, {estimated_components} components")
                    
                except (json.JSONDecodeError, AttributeError) as e:
                     logger.warning(f"Could not parse LLM response as JSON: {str(e)[:100]}")
            
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {str(e)}")
        
        return repo_analysis