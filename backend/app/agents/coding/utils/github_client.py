"""
GitHub Client for pushing generated projects to repositories
"""

import os
import requests
import base64
from typing import Dict, Any, Optional
from pathlib import Path
import json
from urllib.parse import quote

class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("GITHUB_ACCESS_TOKEN", "")
        self.base_url = "https://api.github.com"
        # GitHub API accepts both "token" and "Bearer" formats
        # Using "token" format for personal access tokens
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.access_token:
            self.headers["Authorization"] = f"token {self.access_token}"
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        url = f"{self.base_url}/user/repos"
        data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 422:
            # Repository already exists
            return {"error": "Repository already exists", "status": 422}
        else:
            response.raise_for_status()
    
    def get_file_sha(self, repo_name: str, file_path: str) -> Optional[str]:
        """Get the SHA hash of an existing file in the repository"""
        try:
            username = self.get_username()
            # URL encode the file path to handle special characters
            encoded_path = '/'.join(quote(part, safe='') for part in file_path.split('/'))
            url = f"{self.base_url}/repos/{username}/{repo_name}/contents/{encoded_path}"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("sha")
            elif response.status_code == 404:
                # File doesn't exist
                return None
            else:
                # Other error, return None to try upload anyway
                return None
        except Exception:
            # If we can't check, return None and try upload
            return None
    
    def upload_file(self, repo_name: str, file_path: str, content: bytes, commit_message: str = "Add file", is_binary: bool = False) -> Dict[str, Any]:
        """Upload a single file to repository
        
        Args:
            repo_name: Name of the repository
            file_path: Path to file in repository
            content: File content as bytes
            commit_message: Commit message
            is_binary: Whether the file is binary (affects encoding)
        """
        username = self.get_username()
        # URL encode the file path to handle special characters
        encoded_path = '/'.join(quote(part, safe='') for part in file_path.split('/'))
        url = f"{self.base_url}/repos/{username}/{repo_name}/contents/{encoded_path}"
        
        # Check if file exists and get its SHA
        existing_sha = self.get_file_sha(repo_name, file_path)
        
        # Encode content to base64 (GitHub API requires base64)
        content_encoded = base64.b64encode(content).decode('utf-8')
        
        data = {
            "message": commit_message,
            "content": content_encoded
        }
        
        # Include SHA if file exists (required for updates)
        if existing_sha:
            data["sha"] = existing_sha
        
        response = requests.put(url, headers=self.headers, json=data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            response.raise_for_status()
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary by attempting to read it as text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Read first 1KB
            return False
        except (UnicodeDecodeError, UnicodeError):
            return True
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped"""
        file_str = str(file_path)
        
        # Skip common directories and files
        skip_patterns = [
            '.git', '__pycache__', 'node_modules', '.env',
            '.DS_Store', 'Thumbs.db', '.pytest_cache',
            '.coverage', 'htmlcov', '.mypy_cache',
            'dist', 'build', '.next', '.nuxt', '.cache'
        ]
        
        if any(skip in file_str for skip in skip_patterns):
            return True
        
        # Skip files larger than 50MB (GitHub limit is 100MB, but we'll be conservative)
        try:
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB
                return True
        except (OSError, ValueError):
            return True
        
        return False
    
    def upload_directory(self, repo_name: str, local_dir: Path, commit_message: str = "Initial commit") -> Dict[str, Any]:
        """Upload entire directory to repository"""
        results = []
        
        for file_path in local_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip certain files
            if self._should_skip_file(file_path):
                continue
            
            # Get relative path
            relative_path = file_path.relative_to(local_dir)
            github_path = str(relative_path).replace('\\', '/')
            
            try:
                # Determine if file is binary
                is_binary = self._is_binary_file(file_path)
                
                # Read file content
                if is_binary:
                    # Read binary files as bytes
                    with open(file_path, 'rb') as f:
                        content = f.read()
                else:
                    # Read text files and encode to bytes
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                        content = text_content.encode('utf-8')
                    except UnicodeDecodeError:
                        # Fallback: try with different encoding
                        try:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                text_content = f.read()
                            content = text_content.encode('utf-8')
                        except Exception:
                            # If all else fails, read as binary
                            with open(file_path, 'rb') as f:
                                content = f.read()
                            is_binary = True
                
                # Upload file
                result = self.upload_file(repo_name, github_path, content, commit_message, is_binary)
                results.append({"file": github_path, "status": "success"})
                
            except requests.exceptions.HTTPError as e:
                error_msg = str(e)
                if hasattr(e.response, 'text'):
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('message', str(e))
                    except:
                        error_msg = e.response.text[:200]  # First 200 chars
                results.append({"file": github_path, "status": "error", "error": error_msg})
            except Exception as e:
                results.append({"file": github_path, "status": "error", "error": str(e)})
        
        return {"uploaded_files": results}
    
    def get_username(self) -> str:
        """Get the authenticated user's username"""
        url = f"{self.base_url}/user"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["login"]
    
    def repository_exists(self, repo_name: str) -> bool:
        """Check if repository exists"""
        try:
            username = self.get_username()
            url = f"{self.base_url}/repos/{username}/{repo_name}"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False