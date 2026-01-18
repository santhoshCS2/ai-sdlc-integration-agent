"""
GitHubPublisherAgent - Publishes generated projects to GitHub
"""

from typing import Dict, Any, Optional
from pathlib import Path
from app.agents.coding.utils.github_client import GitHubClient
from app.agents.coding.utils.logger import StreamlitLogger

class GitHubPublisherAgent:
    """Agent that publishes projects to GitHub"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
        self.github_client = GitHubClient()
    
    def publish(self, project_config: Dict[str, Any], project_directory: str) -> Dict[str, Any]:
        """Publish project to GitHub"""
        project_name = project_config["project_name"]
        description = project_config.get("description", "Generated full-stack application")
        
        self.logger.log(f"📤 Publishing project to GitHub: {project_name}")
        
        try:
            # Check if GitHub token is available
            if not self.github_client.access_token:
                self.logger.log("⚠️ No GitHub token found - skipping GitHub publish")
                return {
                    "success": False,
                    "error": "No GitHub access token configured",
                    "skip_reason": "no_token"
                }
            
            # Create repository
            self.logger.log(f"🔨 Creating GitHub repository: {project_name}")
            repo_result = self.github_client.create_repository(
                repo_name=project_name,
                description=f"🚀 {description} | Generated with CODE AGENT",
                private=False
            )
            
            if repo_result.get("error") == "Repository already exists":
                self.logger.log(f"📁 Repository {project_name} already exists - updating files")
            elif "clone_url" in repo_result:
                self.logger.log(f"✅ Repository created: {repo_result['html_url']}")
            
            # Upload project files
            self.logger.log("📁 Uploading project files to GitHub...")
            project_path = Path(project_directory)
            
            upload_result = self.github_client.upload_directory(
                repo_name=project_name,
                local_dir=project_path,
                commit_message="🚀 Initial commit - Generated with CODE AGENT"
            )
            
            uploaded_count = len([f for f in upload_result["uploaded_files"] if f["status"] == "success"])
            error_count = len([f for f in upload_result["uploaded_files"] if f["status"] == "error"])
            failed_files = [f for f in upload_result["uploaded_files"] if f["status"] == "error"]
            
            self.logger.log(f"✅ Uploaded {uploaded_count} files to GitHub")
            if error_count > 0:
                self.logger.log(f"⚠️ {error_count} files failed to upload")
                # Log first few failed files with their errors
                for failed_file in failed_files[:5]:  # Show first 5 failures
                    error_msg = failed_file.get("error", "Unknown error")
                    # Truncate long error messages
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    self.logger.log(f"   ❌ {failed_file['file']}: {error_msg}")
                if len(failed_files) > 5:
                    self.logger.log(f"   ... and {len(failed_files) - 5} more files failed")
            
            # Get repository URL
            username = self.github_client.get_username()
            repo_url = f"https://github.com/{username}/{project_name}"
            
            return {
                "success": True,
                "repository_url": repo_url,
                "uploaded_files": uploaded_count,
                "failed_files": error_count,
                "username": username
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error publishing to GitHub: {str(e)}", level="error")
            return {
                "success": False,
                "error": str(e)
            }