"""
GitHubClonerAgent - Clones frontend code from GitHub repository
"""

import os
import tempfile
import subprocess
from typing import Dict, Any
from pathlib import Path
from app.agents.coding.utils.logger import StreamlitLogger
from app.core.utils import safe_remove_directory

class GitHubClonerAgent:
    """Agent that clones frontend code from GitHub"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def clone_repo(self, project_config: Dict[str, Any]) -> Dict[str, str]:
        """Clone frontend code from GitHub repository"""
        github_url = project_config.get("github_repo_url", "")
        
        if not github_url:
            self.logger.log("❌ No GitHub URL provided", level="error")
            return {}
        
        try:
            # Create temporary directory for cloning
            temp_dir = tempfile.mkdtemp()
            clone_path = Path(temp_dir) / "frontend"
            
            self.logger.log(f"🔄 Cloning repository: {github_url}")
            
            # Clone the repository
            result = subprocess.run([
                "git", "clone", github_url, str(clone_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            # Read all files from the cloned repository
            frontend_files = self._read_repository_files(clone_path)
            
            # Clean up temporary directory with Windows-compatible method
            self._cleanup_temp_dir(temp_dir)
            
            self.logger.log(f"✅ Successfully cloned {len(frontend_files)} files from repository")
            return frontend_files
            
        except subprocess.TimeoutExpired:
            self.logger.log("❌ Git clone timed out", level="error")
            return self._create_fallback_frontend(project_config)
        except FileNotFoundError:
            self.logger.log("❌ Git not found. Please install Git", level="error")
            return self._create_fallback_frontend(project_config)
        except Exception as e:
            error_msg = str(e)
            if "Repository not found" in error_msg or "404" in error_msg or "exit code(128)" in error_msg:
                self.logger.log(f"❌ Repository not found or access denied: {github_url}", level="error")
                self.logger.log("💡 Tip: Check if the repository URL is correct and if it is public. Private repositories require a GitHub token in .env", level="error")
            elif "authentication failed" in error_msg.lower():
                self.logger.log(f"❌ Authentication failed for: {github_url}", level="error")
                self.logger.log("💡 Tip: Check your GITHUB_TOKEN in the .env file", level="error")
            else:
                self.logger.log(f"❌ Failed to clone repository: {error_msg}", level="error")
                
            return self._create_fallback_frontend(project_config)
    
    def _read_repository_files(self, repo_path: Path) -> Dict[str, str]:
        """Read all relevant files from the cloned repository"""
        files = {}
        
        # File extensions to include
        include_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.json', '.html', '.css', '.scss', 
            '.md', '.txt', '.env', '.gitignore', '.yml', '.yaml'
        }
        
        # Directories to skip
        skip_dirs = {'.git', 'node_modules', 'dist', 'build', '.next', 'coverage'}
        
        try:
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    # Skip files in excluded directories
                    if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                        continue
                    
                    # Only include relevant file types
                    if file_path.suffix.lower() in include_extensions or file_path.name in ['package.json', 'README.md']:
                        try:
                            relative_path = file_path.relative_to(repo_path)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                files[str(relative_path)] = f.read()
                        except (UnicodeDecodeError, PermissionError):
                            # Skip binary files or files we can't read
                            continue
                        except Exception:
                            # Skip any problematic files
                            continue
        
        except Exception as e:
            self.logger.log(f"⚠️ Error reading repository files: {str(e)}", level="warning")
        
        return files
    
    def _cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary directory with standard utility"""
        safe_remove_directory(temp_dir)
    
    def _create_fallback_frontend(self, project_config: Dict[str, Any]) -> Dict[str, str]:
        """Create a basic frontend structure when cloning fails"""
        project_name = project_config.get("project_name", "My App")
        
        self.logger.log("⚠️ Creating fallback frontend structure", level="warning")
        
        return {
            "package.json": f'''{{
  "name": "{project_name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^5.0.0"
  }}
}}''',
            "index.html": f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
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
            "src/App.jsx": f'''import React from 'react'

function App() {{
  return (
    <div style={{{{ padding: '20px', fontFamily: 'Arial, sans-serif' }}}}>
      <h1>{project_name}</h1>
      <p>Frontend cloned from GitHub repository</p>
    </div>
  )
}}

export default App''',
            "README.md": f'''# {project_name}

Frontend application cloned from GitHub repository.

## Getting Started

```bash
npm install
npm run dev
```
'''
        }