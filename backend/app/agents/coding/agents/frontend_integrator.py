"""
FrontendIntegratorAgent - Injects API calls into frontend components
"""

from typing import Dict, Any, List
from pathlib import Path
import json
import re
from utils.logger import StreamlitLogger

class FrontendIntegratorAgent:
    """Agent that modifies frontend code to add API connections"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def integrate_api_calls(
        self,
        frontend_path: Path,
        backend_endpoints: List[Dict[str, Any]],
        backend_url: str = "http://localhost:8000"
    ) -> Dict[str, str]:
        """Add API calls to frontend components"""
        self.logger.log("🔗 Integrating API calls into frontend...")
        
        # Detect frontend framework
        framework = self._detect_framework(frontend_path)
        self.logger.log(f"📦 Detected framework: {framework}")
        
        # Add axios dependency
        self._add_axios_dependency(frontend_path)
        
        # Create API service file
        api_service = self._create_api_service(backend_endpoints, backend_url, framework)
        
        # Find and modify components
        modified_files = self._modify_components(frontend_path, backend_endpoints, framework)
        
        self.logger.log(f"✅ Modified {len(modified_files)} frontend files")
        
        return {
            "api_service": api_service,
            "modified_files": modified_files
        }
    
    def _detect_framework(self, frontend_path: Path) -> str:
        """Detect frontend framework from package.json"""
        package_json = frontend_path / "package.json"
        
        if not package_json.exists():
            return "react"  # default
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'next' in deps:
                    return "nextjs"
                elif 'vue' in deps or '@vue/cli' in deps:
                    return "vue"
                elif 'svelte' in deps:
                    return "svelte"
                else:
                    return "react"
        except:
            return "react"
    
    def _add_axios_dependency(self, frontend_path: Path):
        """Add axios to package.json"""
        package_json = frontend_path / "package.json"
        
        if not package_json.exists():
            self.logger.log("⚠️ package.json not found, skipping axios installation")
            return
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add axios if not present
            if 'axios' not in data.get('dependencies', {}):
                if 'dependencies' not in data:
                    data['dependencies'] = {}
                data['dependencies']['axios'] = '^1.6.0'
                
                with open(package_json, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.log("✅ Added axios to package.json")
        except Exception as e:
            self.logger.log(f"⚠️ Could not add axios: {str(e)}")
    
    def _create_api_service(
        self,
        endpoints: List[Dict[str, Any]],
        backend_url: str,
        framework: str
    ) -> str:
        """Create API service file with all endpoints"""
        
        # Generate endpoint functions
        endpoint_functions = []
        for ep in endpoints:
            method = ep.get('method', 'GET').upper()
            path = ep.get('path', '/')
            name = ep.get('name', path.replace('/', '_').strip('_'))
            
            if method == 'GET':
                func = f"""export const {name} = async (params = {{}}) => {{
  const response = await api.get('{path}', {{ params }});
  return response.data;
}};"""
            elif method == 'POST':
                func = f"""export const {name} = async (data) => {{
  const response = await api.post('{path}', data);
  return response.data;
}};"""
            elif method == 'PUT':
                func = f"""export const {name} = async (id, data) => {{
  const response = await api.put(`{path}/${{id}}`, data);
  return response.data;
}};"""
            elif method == 'DELETE':
                func = f"""export const {name} = async (id) => {{
  const response = await api.delete(`{path}/${{id}}`);
  return response.data;
}};"""
            else:
                func = f"""export const {name} = async (data) => {{
  const response = await api.request({{
    method: '{method}',
    url: '{path}',
    data
  }});
  return response.data;
}};"""
            
            endpoint_functions.append(func)
        
        # Create service file content
        service_content = f"""import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '{backend_url}';

// Create axios instance
const api = axios.create({{
  baseURL: API_BASE_URL,
  headers: {{
    'Content-Type': 'application/json',
  }},
}});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {{
    const token = localStorage.getItem('token');
    if (token) {{
      config.headers.Authorization = `Bearer ${{token}}`;
    }}
    return config;
  }},
  (error) => {{
    return Promise.reject(error);
  }}
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {{
    if (error.response?.status === 401) {{
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }}
    return Promise.reject(error);
  }}
);

// Authentication
export const login = async (email, password) => {{
  const response = await api.post('/auth/login', {{ email, password }});
  if (response.data.access_token) {{
    localStorage.setItem('token', response.data.access_token);
  }}
  return response.data;
}};

export const register = async (email, username, password) => {{
  const response = await api.post('/auth/register', {{ email, username, password }});
  if (response.data.access_token) {{
    localStorage.setItem('token', response.data.access_token);
  }}
  return response.data;
}};

export const logout = () => {{
  localStorage.removeItem('token');
  window.location.href = '/login';
}};

// API Endpoints
{chr(10).join(endpoint_functions)}

export default api;
"""
        
        return service_content
    
    def _modify_components(
        self,
        frontend_path: Path,
        endpoints: List[Dict[str, Any]],
        framework: str
    ) -> Dict[str, str]:
        """Find and modify components to use API calls"""
        modified = {}
        
        # Find component files
        src_path = frontend_path / "src"
        if not src_path.exists():
            return modified
        
        # Look for component files
        component_files = []
        for ext in ['.jsx', '.js', '.tsx', '.ts', '.vue']:
            component_files.extend(src_path.rglob(f'*{ext}'))
        
        for comp_file in component_files:
            # Skip node_modules and test files
            if 'node_modules' in str(comp_file) or 'test' in comp_file.name.lower():
                continue
            
            try:
                with open(comp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if component needs API integration
                if self._needs_api_integration(content):
                    self.logger.log(f"  🔍 Analyzing {comp_file.name} for hardcoded elements...")
                    
                    # Log what hardcoded elements were found
                    hardcoded_elements = self._detect_hardcoded_elements(content)
                    if hardcoded_elements:
                        self.logger.log(f"  📋 Found hardcoded elements in {comp_file.name}:")
                        for element in hardcoded_elements:
                            self.logger.log(f"    - {element}")
                    
                    new_content = self._inject_api_calls(content, endpoints, framework)
                    
                    if new_content != content:
                        with open(comp_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        rel_path = comp_file.relative_to(frontend_path)
                        modified[str(rel_path)] = new_content
                        
                        # Log what was changed
                        changes = self._analyze_changes(content, new_content)
                        self.logger.log(f"  ✅ Modified {rel_path}:")
                        for change in changes:
                            self.logger.log(f"    ✓ {change}")
            
            except Exception as e:
                self.logger.log(f"⚠️ Error modifying {comp_file.name}: {str(e)}")
        
        return modified
    
    def _needs_api_integration(self, content: str) -> bool:
        """Check if component needs API integration"""
        # Look for signs that component needs API calls
        indicators = [
            'useState',
            'useEffect',
            'fetch(',
            'TODO',
            'mock',
            'dummy',
            'sample data',
            'hardcoded',
            'const data = [',
            'const items = [',
            'const users = [',
            'static data',
            'placeholder',
            'example data',
            'test data',
            'fake data',
            'demo data',
            'alert(',
            'onClick={() =>',
            'onClick={()=>',
            'onSubmit={() =>',
            'onSubmit={()=>'
        ]
        
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in indicators)
    
    def _inject_api_calls(
        self,
        content: str,
        endpoints: List[Dict[str, Any]],
        framework: str
    ) -> str:
        """Inject API calls into component"""
        
        # Step 1: Add API service imports
        content = self._add_api_imports(content, endpoints)
        
        # Step 2: Remove hardcoded data arrays
        content = self._remove_hardcoded_data(content)
        
        # Step 3: Replace fetch calls with API service calls
        content = self._replace_fetch_calls(content)
        
        # Step 4: Replace non-functional buttons with real handlers
        content = self._replace_button_handlers(content, endpoints)
        
        # Step 5: Add useEffect for data fetching if needed
        if 'useEffect' not in content and 'useState' in content:
            content = self._add_data_fetching(content, endpoints)
        
        # Step 6: Add error handling and loading states
        content = self._add_error_handling(content)
        
        return content
    
    def _add_api_imports(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add API service imports based on endpoints"""
        # Extract function names from endpoints
        import_functions = ['login', 'register', 'logout']
        
        for ep in endpoints:
            if 'name' in ep:
                import_functions.append(ep['name'])
            else:
                # Generate function name from path and method
                path = ep.get('path', '').replace('/api/', '').replace('/', '')
                method = ep.get('method', 'GET').lower()
                if method == 'get':
                    import_functions.append(f'get{path.capitalize()}')
                elif method == 'post':
                    import_functions.append(f'create{path.capitalize()}')
                elif method == 'put':
                    import_functions.append(f'update{path.capitalize()}')
                elif method == 'delete':
                    import_functions.append(f'delete{path.capitalize()}')
        
        # Remove duplicates
        import_functions = list(set(import_functions))
        
        # Add import statement if not present
        if 'from' in content and './services/api' not in content:
            # Find the last import statement
            import_pattern = r'(import .+ from .+;?\n)'
            imports = re.findall(import_pattern, content)
            
            if imports:
                last_import = imports[-1]
                api_import = f"import {{ {', '.join(import_functions[:10])} }} from './services/api';\n"
                content = content.replace(last_import, last_import + api_import)
            else:
                # Add at the beginning if no imports found
                api_import = f"import {{ {', '.join(import_functions[:10])} }} from './services/api';\n\n"
                content = api_import + content
        
        return content
    
    def _remove_hardcoded_data(self, content: str) -> str:
        """Remove hardcoded data arrays and replace with empty state"""
        import re
        
        # Pattern 1: const data = [array of objects]
        pattern1 = r'const\s+(\w+)\s*=\s*\[\s*\{[^\]]+\]\s*;'
        matches1 = re.findall(pattern1, content, re.DOTALL)
        
        for var_name in matches1:
            # Replace with empty array and useState
            old_pattern = rf'const\s+{var_name}\s*=\s*\[[^\]]+\]\s*;'
            new_code = f'const [{var_name}, set{var_name.capitalize()}] = useState([]);'
            content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
        
        # Pattern 2: const items = [{...}, {...}]
        pattern2 = r'const\s+(\w+)\s*=\s*\[\s*\{[^}]+\}[^\]]*\]\s*;'
        matches2 = re.findall(pattern2, content, re.DOTALL)
        
        for var_name in matches2:
            if var_name not in matches1:  # Avoid duplicates
                old_pattern = rf'const\s+{var_name}\s*=\s*\[[^\]]+\]\s*;'
                new_code = f'const [{var_name}, set{var_name.capitalize()}] = useState([]);'
                content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
        
        # Pattern 3: Simple arrays like const data = ['item1', 'item2']
        pattern3 = r'const\s+(\w+)\s*=\s*\[[^\]]*["\'][^\]]*\]\s*;'
        matches3 = re.findall(pattern3, content)
        
        for var_name in matches3:
            if var_name not in matches1 and var_name not in matches2:
                old_pattern = rf'const\s+{var_name}\s*=\s*\[[^\]]*\]\s*;'
                new_code = f'const [{var_name}, set{var_name.capitalize()}] = useState([]);'
                content = re.sub(old_pattern, new_code, content)
        
        return content
    
    def _replace_button_handlers(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Replace non-functional button handlers with real API calls"""
        import re
        
        # Replace console.log handlers
        content = re.sub(
            r'onClick=\{\(\)\s*=>\s*console\.log\([^}]+\)\}',
            'onClick={handleClick}',
            content
        )
        
        # Replace alert handlers
        content = re.sub(
            r'onClick=\{\(\)\s*=>\s*alert\([^}]+\)\}',
            'onClick={handleSubmit}',
            content
        )
        
        # Replace empty arrow functions
        content = re.sub(
            r'onClick=\{\(\)\s*=>\s*\{\s*\}\}',
            'onClick={handleClick}',
            content
        )
        
        # Add handler functions if they don't exist
        if 'handleClick' in content and 'const handleClick' not in content:
            # Find appropriate POST endpoint for handleClick
            post_endpoint = None
            for ep in endpoints:
                if ep.get('method', '').upper() == 'POST':
                    post_endpoint = ep
                    break
            
            endpoint_name = post_endpoint.get('name', 'createItem') if post_endpoint else 'createItem'
            
            handler_code = f"""
  const handleClick = async () => {{
    try {{
      setLoading(true);
      const result = await {endpoint_name}(formData);
      setData([...data, result]);
      setError(null);
    }} catch (error) {{
      console.error('Error:', error);
      setError(error.message);
    }} finally {{
      setLoading(false);
    }}
  }};
"""
            
            # Insert before the return statement
            return_pattern = r'(\s+return\s*\(?)'
            content = re.sub(return_pattern, handler_code + r'\1', content, count=1)
        
        return content
    
    def _add_error_handling(self, content: str) -> str:
        """Add error handling and loading states"""
        import re
        
        # Add loading and error state if useState is present but these states are missing
        if 'useState' in content:
            if 'loading' not in content.lower():
                # Find the first useState
                usestate_pattern = r'(const \[[^\]]+\] = useState\([^)]+\);)'
                first_usestate = re.search(usestate_pattern, content)
                
                if first_usestate:
                    loading_state = '\n  const [loading, setLoading] = useState(false);'
                    content = content.replace(first_usestate.group(1), first_usestate.group(1) + loading_state)
            
            if 'error' not in content.lower() or 'setError' not in content:
                # Find the first useState
                usestate_pattern = r'(const \[[^\]]+\] = useState\([^)]+\);)'
                first_usestate = re.search(usestate_pattern, content)
                
                if first_usestate:
                    error_state = '\n  const [error, setError] = useState(null);'
                    content = content.replace(first_usestate.group(1), first_usestate.group(1) + error_state)
        
        return content
    
    def _detect_hardcoded_elements(self, content: str) -> List[str]:
        """Detect and list hardcoded elements in the component"""
        elements = []
        
        # Check for hardcoded data arrays
        if re.search(r'const\s+\w+\s*=\s*\[\s*\{', content):
            elements.append("Hardcoded data arrays")
        
        # Check for console.log in handlers
        if re.search(r'onClick=\{[^}]*console\.log', content):
            elements.append("Console.log button handlers")
        
        # Check for alert in handlers
        if re.search(r'onClick=\{[^}]*alert\(', content):
            elements.append("Alert button handlers")
        
        # Check for empty handlers
        if re.search(r'onClick=\{\(\)\s*=>\s*\{\s*\}\}', content):
            elements.append("Empty button handlers")
        
        # Check for fetch calls
        if 'fetch(' in content:
            elements.append("Direct fetch() calls")
        
        # Check for mock/dummy data
        content_lower = content.lower()
        if any(word in content_lower for word in ['mock', 'dummy', 'sample data', 'test data']):
            elements.append("Mock/dummy data")
        
        return elements
    
    def _analyze_changes(self, old_content: str, new_content: str) -> List[str]:
        """Analyze what changes were made to the component"""
        changes = []
        
        # Check if API imports were added
        if './services/api' in new_content and './services/api' not in old_content:
            changes.append("Added API service imports")
        
        # Check if hardcoded arrays were replaced
        old_arrays = len(re.findall(r'const\s+\w+\s*=\s*\[\s*\{', old_content))
        new_arrays = len(re.findall(r'const\s+\w+\s*=\s*\[\s*\{', new_content))
        if old_arrays > new_arrays:
            changes.append(f"Replaced {old_arrays - new_arrays} hardcoded data arrays with useState")
        
        # Check if useEffect was added
        if 'useEffect' in new_content and 'useEffect' not in old_content:
            changes.append("Added useEffect for data fetching")
        
        # Check if error handling was added
        if 'setError' in new_content and 'setError' not in old_content:
            changes.append("Added error handling state")
        
        # Check if loading state was added
        if 'setLoading' in new_content and 'setLoading' not in old_content:
            changes.append("Added loading state")
        
        # Check if handlers were replaced
        old_console = len(re.findall(r'console\.log', old_content))
        new_console = len(re.findall(r'console\.log', new_content))
        if old_console > new_console:
            changes.append("Replaced console.log handlers with real API calls")
        
        return changes
    
    def _replace_fetch_calls(self, content: str) -> str:
        """Replace fetch() calls with API service calls"""
        
        # Pattern: fetch('url')
        fetch_pattern = r"fetch\(['\"]([^'\"]+)['\"]\)"
        
        def replace_fetch(match):
            url = match.group(1)
            # Convert to API service call
            return f"api.get('{url}')"
        
        content = re.sub(fetch_pattern, replace_fetch, content)
        
        return content
    
    def _add_data_fetching(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add useEffect hook for data fetching"""
        
        # Find component function
        component_pattern = r'(function|const) (\w+)\s*\('
        match = re.search(component_pattern, content)
        
        if not match:
            return content
        
        # Add useEffect after useState declarations
        usestate_pattern = r'(const \[.+\] = useState\(.+\);)'
        usestates = re.findall(usestate_pattern, content)
        
        if usestates:
            last_usestate = usestates[-1]
            
            # Find appropriate GET endpoint
            get_endpoint = None
            for ep in endpoints:
                if ep.get('method', '').upper() == 'GET':
                    get_endpoint = ep
                    break
            
            endpoint_path = get_endpoint.get('path', '/api/items') if get_endpoint else '/api/items'
            endpoint_name = get_endpoint.get('name', 'getItems') if get_endpoint else 'getItems'
            
            # Create useEffect hook with real endpoint
            useeffect = f"""
  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        setLoading(true);
        const data = await {endpoint_name}();
        setData(data);
        setError(null);
      }} catch (error) {{
        console.error('Error fetching data:', error);
        setError(error.message);
      }} finally {{
        setLoading(false);
      }}
    }};
    
    fetchData();
  }}, []);
"""
            
            content = content.replace(last_usestate, last_usestate + useeffect)
        
        return content
