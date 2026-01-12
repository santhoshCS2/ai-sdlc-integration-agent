"""
FrontendGeneratorAgent - Generates pixel-perfect, responsive frontend code matching selected stack + Figma design
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
import json
from utils.logger import StreamlitLogger

class FrontendGeneratorAgent:
    """Agent that generates frontend code"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def generate(self, project_spec: Dict[str, Any], figma_data: Dict[str, Any], frontend_stack: str) -> Dict[str, str]:
        """Generate frontend code based on spec and Figma design"""
        self.logger.log(f"⚛️ Generating {frontend_stack} frontend code...")
        
        # Prepare design context (handle None figma_data)
        if figma_data is None:
            figma_data = {}
        design_context = self._prepare_design_context(figma_data)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate production-ready frontend code as JSON. Return ONLY valid JSON, no markdown.

Requirements:
- Match Figma design colors and typography
- Create responsive mobile-first components
- Use: react@^18.0.0, vite@^5.0.0, tailwindcss
- Include TypeScript types
- Reusable components with routing

Return JSON: {"file_path": "code content", ...}
Include: package.json, index.html, App.jsx, components, styles, vite.config.js, README"""),
            ("human", "Project: {project_spec}\nDesign: {design_context}\nStack: {frontend_stack}\nGenerate frontend code as JSON only.")
        ])
        
        # Retry logic to ensure we get LLM-generated code
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                messages = prompt.format_messages(
                    project_spec=json.dumps(project_spec, indent=2),
                    design_context=json.dumps(design_context, indent=2),
                    frontend_stack=frontend_stack
                )
                
                self.logger.log(f"🤖 Calling LLM to generate frontend code (attempt {attempt + 1}/{max_retries})...")
                
                try:
                    response = self.llm.invoke(messages)
                except Exception as llm_err:
                    error_msg = str(llm_err)
                    self.logger.log(f"⚠️ LLM API call failed: {error_msg}", level="error")
                    last_error = llm_err
                    
                    # Check for specific errors
                    if "401" in error_msg or "Unauthorized" in error_msg:
                        self.logger.log("❌ Authentication failed - check your API keys", level="error")
                        raise Exception(f"LLM API Authentication failed: {error_msg}")
                    elif "429" in error_msg or "rate limit" in error_msg.lower():
                        self.logger.log("⚠️ Rate limited - waiting before retry...", level="error")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(5)  # Wait 5 seconds before retrying
                            continue
                    elif "503" in error_msg or "Service Unavailable" in error_msg:
                        self.logger.log("⚠️ LLM service temporarily unavailable", level="error")
                        if attempt < max_retries - 1:
                            continue
                    
                    raise
                
                content = response.content.strip()
                
                if not content:
                    raise ValueError("LLM returned empty response")
                
                self.logger.log(f"📦 Processing LLM response ({len(content)} chars)...")
                
                # Parse JSON from response with comprehensive cleaning
                frontend_code = self._parse_json_response(content)
                if not frontend_code:
                    # Create minimal frontend code as fallback
                    self.logger.log("JSON parsing failed, creating minimal frontend...", level="warning")
                    frontend_code = self._create_minimal_frontend(project_spec, frontend_stack)
                
                # Validate we got actual code files
                if not isinstance(frontend_code, dict) or len(frontend_code) < 3:
                    raise ValueError(f"LLM response doesn't contain enough files (got {len(frontend_code) if isinstance(frontend_code, dict) else 0})")
                
                file_count = len(frontend_code)
                self.logger.log(f"✅ Generated {file_count} frontend files from LLM")
                
                return frontend_code
                
            except json.JSONDecodeError as e:
                last_error = e
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
                        frontend_code = self._parse_json_response(content)
                        if frontend_code and isinstance(frontend_code, dict) and len(frontend_code) >= 3:
                            self.logger.log(f"✅ Generated {len(frontend_code)} frontend files after JSON fix")
                            return frontend_code
                    except Exception as fix_err:
                        self.logger.log(f"⚠️ Failed to fix JSON: {str(fix_err)}", level="error")
                        continue
                else:
                    self.logger.log(f"❌ Failed to parse JSON after {max_retries} attempts", level="error")
                    
            except Exception as e:
                last_error = e
                error_msg = str(e)
                self.logger.log(f"⚠️ Error generating frontend (attempt {attempt + 1}/{max_retries}): {error_msg}", level="error")
                if attempt == max_retries - 1:
                    # Last attempt failed - use fallback
                    self.logger.log("Using minimal frontend fallback...", level="warning")
                    return self._create_minimal_frontend(project_spec, frontend_stack)
        
        # Should never reach here, but if we do, use fallback
        self.logger.log("All attempts failed, using minimal frontend fallback...", level="warning")
        return self._create_minimal_frontend(project_spec, frontend_stack)
    
    def _create_minimal_frontend(self, project_spec: Dict[str, Any], frontend_stack: str) -> Dict[str, str]:
        """Create minimal frontend code when JSON parsing fails"""
        project_name = project_spec.get("overview", "My App").split(":")[0]
        
        return {
            "package.json": '''{
  "name": "''' + project_name.lower().replace(" ", "-") + '''",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^5.0.0"
  }
}''',
            "index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + project_name + '''</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>''',
            "src/main.jsx": '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''',
            "src/App.jsx": '''import React from 'react'

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>''' + project_name + '''</h1>
      <p>Welcome to your new application!</p>
      <div style={{ marginTop: '20px' }}>
        <button onClick={() => alert('Hello World!')}>Click Me</button>
      </div>
    </div>
  )
}

export default App''',
            "vite.config.js": '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})''',
            "README.md": f'''# {project_name}

A React application built with Vite.

## Getting Started

```bash
npm install
npm run dev
```
'''
        }
    
    def _parse_json_response(self, content: str) -> Dict[str, str]:
        """Parse JSON from LLM response with comprehensive cleaning"""
        import json
        import re
        import html
        
        try:
            # Step 1: Clean up HTML entities
            content = html.unescape(content)
            
            # Step 2: Remove BOM and invisible characters
            content = content.strip('\ufeff').strip()
            
            # Step 3: Extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    content = json_match.group(0)
            
            # Step 4: Fix common JSON issues
            # Fix escaped quotes
            content = content.replace('\\"', '"')
            # Fix double backslashes
            content = content.replace('\\\\', '\\')
            # Fix single quotes (convert to double quotes)
            content = re.sub(r"(?<!\\)'([^']*?)(?<!\\)'", r'"\1"', content)
            # Fix trailing commas
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            
            # Step 5: Try to parse
            result = json.loads(content)
            if isinstance(result, dict):
                return result
            return None
            
        except Exception as e:
            self.logger.log(f"JSON parsing failed: {str(e)}", level="error")
            return None
    
    def _prepare_design_context(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare design context from Figma data"""
        design_tokens = figma_data.get("design_tokens", {})
        return {
            "colors": design_tokens.get("colors", []),
            "typography": design_tokens.get("typography", []),
            "components": design_tokens.get("components", []),
            "frames": design_tokens.get("frames", [])
        }