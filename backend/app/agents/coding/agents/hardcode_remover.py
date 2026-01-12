"""
HardcodeRemoverAgent - Specialized agent for detecting and removing hardcoded elements
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import re
import json
from utils.logger import StreamlitLogger

class HardcodeRemoverAgent:
    """Agent specialized in detecting and removing hardcoded elements from frontend code"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def analyze_and_remove_hardcode(
        self,
        frontend_path: Path,
        endpoints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze frontend for hardcoded elements and remove them"""
        
        self.logger.log("🔍 Starting comprehensive hardcode analysis...")
        
        analysis_results = {
            "files_analyzed": 0,
            "files_modified": 0,
            "hardcoded_elements_found": [],
            "transformations_applied": [],
            "modified_files": {}
        }
        
        # Find all component files
        component_files = self._find_component_files(frontend_path)
        analysis_results["files_analyzed"] = len(component_files)
        
        for comp_file in component_files:
            try:
                with open(comp_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # Analyze hardcoded elements
                hardcoded_elements = self._detect_all_hardcoded_elements(original_content, comp_file.name)
                
                if hardcoded_elements:
                    analysis_results["hardcoded_elements_found"].extend(hardcoded_elements)
                    
                    self.logger.log(f"📄 {comp_file.name}: Found {len(hardcoded_elements)} hardcoded elements")
                    for element in hardcoded_elements:
                        self.logger.log(f"  ❌ {element['type']}: {element['description']}")
                    
                    # Remove hardcoded elements
                    modified_content = self._remove_all_hardcoded_elements(
                        original_content, 
                        hardcoded_elements, 
                        endpoints,
                        comp_file.name
                    )
                    
                    if modified_content != original_content:
                        # Write modified file
                        with open(comp_file, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        
                        rel_path = comp_file.relative_to(frontend_path)
                        analysis_results["modified_files"][str(rel_path)] = modified_content
                        analysis_results["files_modified"] += 1
                        
                        # Log transformations
                        transformations = self._analyze_transformations(original_content, modified_content)
                        analysis_results["transformations_applied"].extend(transformations)
                        
                        self.logger.log(f"✅ {comp_file.name}: Applied {len(transformations)} transformations")
                        for transform in transformations:
                            self.logger.log(f"  ✓ {transform}")
                
            except Exception as e:
                self.logger.log(f"⚠️ Error processing {comp_file.name}: {str(e)}", level="warning")
        
        # Summary
        self.logger.log(f"📊 Hardcode Removal Summary:")
        self.logger.log(f"  📁 Files analyzed: {analysis_results['files_analyzed']}")
        self.logger.log(f"  ✏️ Files modified: {analysis_results['files_modified']}")
        self.logger.log(f"  🔍 Hardcoded elements found: {len(analysis_results['hardcoded_elements_found'])}")
        self.logger.log(f"  🔄 Transformations applied: {len(analysis_results['transformations_applied'])}")
        
        return analysis_results
    
    def _find_component_files(self, frontend_path: Path) -> List[Path]:
        """Find all component files in the frontend"""
        component_files = []
        src_path = frontend_path / "src"
        
        if not src_path.exists():
            return component_files
        
        # Look for component files
        for ext in ['.jsx', '.js', '.tsx', '.ts', '.vue']:
            component_files.extend(src_path.rglob(f'*{ext}'))
        
        # Filter out node_modules and test files
        filtered_files = []
        for file in component_files:
            if 'node_modules' not in str(file) and 'test' not in file.name.lower():
                filtered_files.append(file)
        
        return filtered_files
    
    def _detect_all_hardcoded_elements(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Detect all types of hardcoded elements"""
        elements = []
        
        # 1. Hardcoded data arrays
        array_patterns = [
            (r'const\s+(\w+)\s*=\s*\[\s*\{[^\]]+\]\s*;', "Hardcoded object array"),
            (r'const\s+(\w+)\s*=\s*\[[^\]]*["\'][^\]]*\]\s*;', "Hardcoded string array"),
            (r'const\s+(\w+)\s*=\s*\[\s*\d+[^\]]*\]\s*;', "Hardcoded number array")
        ]
        
        for pattern, description in array_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                elements.append({
                    "type": "hardcoded_data",
                    "description": f"{description}: {match.group(1)}",
                    "variable_name": match.group(1),
                    "line_start": content[:match.start()].count('\n') + 1,
                    "original_code": match.group(0)
                })
        
        # 2. Non-functional button handlers
        button_patterns = [
            (r'onClick=\{[^}]*console\.log[^}]*\}', "Console.log button handler"),
            (r'onClick=\{[^}]*alert\([^}]*\}', "Alert button handler"),
            (r'onClick=\{\(\)\s*=>\s*\{\s*\}\}', "Empty button handler"),
            (r'onSubmit=\{[^}]*console\.log[^}]*\}', "Console.log form handler"),
            (r'onSubmit=\{[^}]*alert\([^}]*\}', "Alert form handler")
        ]
        
        for pattern, description in button_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                elements.append({
                    "type": "non_functional_handler",
                    "description": description,
                    "line_start": content[:match.start()].count('\n') + 1,
                    "original_code": match.group(0)
                })
        
        # 3. Direct fetch calls (should use API service)
        fetch_matches = re.finditer(r'fetch\([^)]+\)', content)
        for match in fetch_matches:
            elements.append({
                "type": "direct_fetch",
                "description": "Direct fetch() call",
                "line_start": content[:match.start()].count('\n') + 1,
                "original_code": match.group(0)
            })
        
        # 4. Mock/dummy data references
        mock_patterns = [
            (r'["\']mock[^"\']*["\']', "Mock data reference"),
            (r'["\']dummy[^"\']*["\']', "Dummy data reference"),
            (r'["\']sample[^"\']*["\']', "Sample data reference"),
            (r'["\']test[^"\']*["\']', "Test data reference")
        ]
        
        for pattern, description in mock_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                elements.append({
                    "type": "mock_data",
                    "description": f"{description}: {match.group(0)}",
                    "line_start": content[:match.start()].count('\n') + 1,
                    "original_code": match.group(0)
                })
        
        # 5. Static URLs (should be environment variables)
        url_matches = re.finditer(r'["\']https?://[^"\']+["\']', content)
        for match in url_matches:
            if 'localhost' not in match.group(0) and 'example.com' not in match.group(0):
                elements.append({
                    "type": "hardcoded_url",
                    "description": f"Hardcoded URL: {match.group(0)}",
                    "line_start": content[:match.start()].count('\n') + 1,
                    "original_code": match.group(0)
                })
        
        return elements
    
    def _remove_all_hardcoded_elements(
        self, 
        content: str, 
        elements: List[Dict[str, Any]], 
        endpoints: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """Remove all detected hardcoded elements"""
        
        modified_content = content
        
        # Group elements by type for efficient processing
        elements_by_type = {}
        for element in elements:
            element_type = element["type"]
            if element_type not in elements_by_type:
                elements_by_type[element_type] = []
            elements_by_type[element_type].append(element)
        
        # 1. Replace hardcoded data arrays with useState
        if "hardcoded_data" in elements_by_type:
            modified_content = self._replace_hardcoded_arrays(modified_content, elements_by_type["hardcoded_data"])
        
        # 2. Replace non-functional handlers with real API calls
        if "non_functional_handler" in elements_by_type:
            modified_content = self._replace_handlers(modified_content, elements_by_type["non_functional_handler"], endpoints)
        
        # 3. Replace direct fetch calls with API service calls
        if "direct_fetch" in elements_by_type:
            modified_content = self._replace_fetch_calls(modified_content, elements_by_type["direct_fetch"])
        
        # 4. Add necessary imports (DO THIS BEFORE state hooks to ensure useState is available)
        modified_content = self._add_necessary_imports(modified_content, endpoints)
        
        # 5. Add state hooks for new state variables
        modified_content = self._add_state_hooks(modified_content)
        
        # 6. Add useEffect for data fetching
        modified_content = self._add_data_fetching_effect(modified_content, endpoints)
        
        return modified_content

    def _replace_hardcoded_arrays(self, content: str, elements: List[Dict[str, Any]]) -> str:
        """Replace hardcoded arrays with useState hooks"""
        
        for element in elements:
            var_name = element.get("variable_name")
            if var_name:
                # Check if it's already a state (don't replace if it looks like useState)
                if f"useState(" in content and f"set{var_name.capitalize()}" in content:
                    continue
                
                # Replace const varName = [...] with const [varName, setVarName] = useState([])
                # Improved regex to handle various spacing and potential trailing comments
                old_pattern = rf'const\s+{var_name}\s*=\s*\[[\s\S]*?\]\s*;'
                new_code = f'const [{var_name}, set{var_name.capitalize()}] = useState([]);'
                content = re.sub(old_pattern, new_code, content)
        
        return content
    
    def _replace_handlers(self, content: str, elements: List[Dict[str, Any]], endpoints: List[Dict[str, Any]]) -> str:
        """Replace non-functional handlers with real API calls"""
        
        # Replace console.log and alert handlers
        content = re.sub(
            r'onClick=\{[^}]*console\.log[^}]*\}',
            'onClick={handleClick}',
            content
        )
        
        content = re.sub(
            r'onClick=\{[^}]*alert\([^}]*\}',
            'onClick={handleSubmit}',
            content
        )
        
        content = re.sub(
            r'onClick=\{\(\)\s*=>\s*\{\s*\}\}',
            'onClick={handleClick}',
            content
        )
        
        # Add handler functions if they're referenced but not defined
        if 'handleClick' in content and 'const handleClick' not in content:
            content = self._add_click_handler(content, endpoints)
        
        if 'handleSubmit' in content and 'const handleSubmit' not in content:
            content = self._add_submit_handler(content, endpoints)
        
        return content
    
    def _add_click_handler(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add a real click handler function"""
        
        # Find appropriate endpoint
        post_endpoint = next((ep for ep in endpoints if ep.get('method', '').upper() == 'POST'), None)
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
        
        # Insert before return statement
        return_pattern = r'(\s+return\s*\(?)'
        content = re.sub(return_pattern, handler_code + r'\1', content, count=1)
        
        return content
    
    def _add_submit_handler(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add a real submit handler function"""
        
        # Find appropriate endpoint
        post_endpoint = next((ep for ep in endpoints if ep.get('method', '').upper() == 'POST'), None)
        endpoint_name = post_endpoint.get('name', 'createItem') if post_endpoint else 'createItem'
        
        handler_code = f"""
  const handleSubmit = async (e) => {{
    e.preventDefault();
    try {{
      setLoading(true);
      const result = await {endpoint_name}(formData);
      setData([...data, result]);
      setFormData({{}});
      setError(null);
    }} catch (error) {{
      console.error('Error:', error);
      setError(error.message);
    }} finally {{
      setLoading(false);
    }}
  }};
"""
        
        # Insert before return statement
        return_pattern = r'(\s+return\s*\(?)'
        content = re.sub(return_pattern, handler_code + r'\1', content, count=1)
        
        return content
    
    def _replace_fetch_calls(self, content: str, elements: List[Dict[str, Any]]) -> str:
        """Replace direct fetch calls with API service calls"""
        
        # Simple replacement for now
        content = re.sub(
            r'fetch\([\'"]([^\'"]+)[\'"]\)',
            r"api.get('\1')",
            content
        )
        
        return content
    
    def _add_necessary_imports(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add necessary imports for API service and React hooks"""
        
        # Handle React hooks imports
        needed_hooks = []
        if 'useState' in content and 'useState' not in content[:content.find('export') if 'export' in content else len(content)]:
            needed_hooks.append('useState')
        if 'useEffect' in content and 'useEffect' not in content[:content.find('export') if 'export' in content else len(content)]:
            needed_hooks.append('useEffect')
        
        if needed_hooks:
            # Look for existing React import
            react_import_match = re.search(r'import\s+(?:React,\s+)?\{([^}]+)\}\s+from\s+[\'"]react[\'"]', content)
            if react_import_match:
                existing_hooks = [h.strip() for h in react_import_match.group(1).split(',')]
                new_hooks = existing_hooks.copy()
                for hook in needed_hooks:
                    if hook not in new_hooks:
                        new_hooks.append(hook)
                
                if len(new_hooks) > len(existing_hooks):
                    old_import = react_import_match.group(0)
                    # Preserve React if it was there
                    if 'React,' in old_import:
                        new_import = f"import React, {{ {', '.join(new_hooks)} }} from 'react'"
                    else:
                        new_import = f"import {{ {', '.join(new_hooks)} }} from 'react'"
                    content = content.replace(old_import, new_import)
            else:
                # Try simple React import: import React from 'react'
                simple_react_match = re.search(r'import\s+React\s+from\s+[\'"]react[\'"]', content)
                if simple_react_match:
                    old_import = simple_react_match.group(0)
                    new_import = f"import React, {{ {', '.join(needed_hooks)} }} from 'react'"
                    content = content.replace(old_import, new_import)
                else:
                    # No react import found at all? Add it at the top
                    content = f"import {{ {', '.join(needed_hooks)} }} from 'react';\n" + content

        # Add API service import if needed
        if ('handleClick' in content or 'handleSubmit' in content or 'api.' in content or 'fetchData' in content) and './services/api' not in content:
            # Generate import functions from endpoints
            import_functions = ['login', 'register', 'logout']
            for ep in endpoints:
                if 'name' in ep:
                    import_functions.append(ep['name'])
            
            # Remove duplicates and limit
            import_functions = list(set(import_functions))[:15]
            
            # Find last import to append after
            imports = re.findall(r'^import\s+.*?;?\n', content, re.MULTILINE)
            if imports:
                last_import = imports[-1]
                api_import = f"import {{ {', '.join(import_functions)} }} from './services/api';\n"
                content = content.replace(last_import, last_import + api_import)
            else:
                api_import = f"import {{ {', '.join(import_functions)} }} from './services/api';\n\n"
                content = api_import + content
        
        return content
    
    def _add_state_hooks(self, content: str) -> str:
        """Add necessary useState hooks for loading and error states"""
        
        if 'useState' in content:
            # Add loading state if setLoading is used but not defined
            if 'setLoading' in content and not re.search(r'const\s+\[loading,\s*setLoading\]\s*=\s*useState', content):
                # Find the first useState to insert after
                first_usestate = re.search(r'(const \[[^\]]+\] = useState\([^)]+\);)', content)
                if first_usestate:
                    loading_state = '\n  const [loading, setLoading] = useState(false);'
                    content = content.replace(first_usestate.group(1), first_usestate.group(1) + loading_state)
            
            # Add error state if setError is used but not defined
            if 'setError' in content and not re.search(r'const\s+\[error,\s*setError\]\s*=\s*useState', content):
                first_usestate = re.search(r'(const \[[^\]]+\] = useState\([^)]+\);)', content)
                if first_usestate:
                    error_state = '\n  const [error, setError] = useState(null);'
                    content = content.replace(first_usestate.group(1), first_usestate.group(1) + error_state)
        
        return content
    
    def _add_data_fetching_effect(self, content: str, endpoints: List[Dict[str, Any]]) -> str:
        """Add useEffect for data fetching if needed"""
        
        # Only add if useEffect is imported and not already used for fetching
        if 'useEffect' in content and 'fetchData' not in content:
            # Find GET endpoint
            get_endpoint = next((ep for ep in endpoints if ep.get('method', '').upper() == 'GET'), None)
            endpoint_name = get_endpoint.get('name', 'getItems') if get_endpoint else 'getItems'
            
            # Find last useState to insert after
            last_usestate = None
            for match in re.finditer(r'(const \[[^\]]+\] = useState\([^)]+\);)', content):
                last_usestate = match
            
            if last_usestate:
                useeffect_code = f"""
  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        setLoading(true);
        const result = await {endpoint_name}();
        // Try to find the data setter (setData, setUsers, etc)
        {"setData(result);" if "setData" in content else "// TODO: set state with result"}
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
                content = content.replace(last_usestate.group(1), last_usestate.group(1) + useeffect_code)
        
        return content
    
    def _analyze_transformations(self, old_content: str, new_content: str) -> List[str]:
        """Analyze what transformations were applied"""
        transformations = []
        
        # Check for useState additions
        old_usestate_count = len(re.findall(r'useState', old_content))
        new_usestate_count = len(re.findall(r'useState', new_content))
        if new_usestate_count > old_usestate_count:
            transformations.append(f"Added {new_usestate_count - old_usestate_count} useState hooks")
        
        # Check for useEffect additions
        if 'useEffect' in new_content and 'useEffect' not in old_content:
            transformations.append("Added useEffect for data fetching")
        
        # Check for API imports
        if './services/api' in new_content and './services/api' not in old_content:
            transformations.append("Added API service imports")
        
        # Check for handler replacements
        old_console_count = len(re.findall(r'console\.log', old_content))
        new_console_count = len(re.findall(r'console\.log', new_content))
        if old_console_count > new_console_count:
            transformations.append("Replaced console.log handlers with API calls")
        
        # Check for hardcoded array replacements
        old_arrays = len(re.findall(r'const\s+\w+\s*=\s*\[', old_content))
        new_arrays = len(re.findall(r'const\s+\w+\s*=\s*\[', new_content))
        if old_arrays > new_arrays:
            transformations.append(f"Replaced {old_arrays - new_arrays} hardcoded arrays with state")
        
        return transformations