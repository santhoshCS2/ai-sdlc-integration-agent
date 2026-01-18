import logging
import os
import shutil
import uuid
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

from app.agents.coding.workflow.orchestrator import ProjectOrchestrator

logger = logging.getLogger(__name__)

class CodingService:
    def __init__(self):
        self.name = "Software Development Agent"
        self.orchestrator = ProjectOrchestrator()

    async def generate_code(self, prd_content: str, architecture_content: str, github_url: str = "") -> str:
        """
        Generates full-stack code based on PRD and Architecture output.
        Adapts the ProjectOrchestrator for the SDLC flow.
        """
        logger.info(f"[{self.name}] Starting code generation for {github_url}")
        
        # Analyze github_url to get project name
        project_name = "generated_project"
        if github_url:
            parts = github_url.strip("/").split("/")
            if len(parts) >= 2:
                project_name = parts[-1].replace(".git", "")

        # Prepare config for orchestrator
        project_config = {
            "project_name": project_name,
            "description": f"Full-stack application for {project_name}",
            "frontend_stack": "React",
            "backend_stack": "FastAPI + SQLAlchemy", # Default professional stack
            "github_repo_url": github_url,
            "publish_to_github": False, # SDLC orchestrator handles pushing separately
            "prd_file_content": prd_content,
            "impact_file_content": architecture_content, # Using architecture/impact as input
            "impact_file_name": "impact_analysis_report.md"
        }

        try:
            # Run the orchestrator
            # Note: generate_project is synchronous in the orchestrator, so we might need to run it in thread pool if it blocks
            # But for now, direct call (it calls LLMs which are usually async, but the orchestrator method itself isn't async def? 
            # checking orchestrator.py: generate_project is def, not async def.
            # However, it likely makes blocking network calls if not using async LLM client properly inside.
            # We'll run it directly for now.
            
            result = self.orchestrator.generate_project(project_config)
            
            if result.get("success"):
                project_dir = result.get("project_directory")
                logger.info(f"[{self.name}] Code generated at: {project_dir}")
                return project_dir
            else:
                logger.error(f"[{self.name}] Code generation failed: {result.get('error')}")
                raise Exception(f"Code generation failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"[{self.name}] Error in generate_code: {e}")
            raise

    def zip_generated_code(self, code_dir: str) -> str:
        """
        Zips the generated code directory for download.
        """
        if not os.path.exists(code_dir):
            raise FileNotFoundError(f"Code directory not found: {code_dir}")
            
        # Create a zip file
        zip_filename = f"project_code_{uuid.uuid4()}"
        zip_path = shutil.make_archive(
            os.path.join(tempfile.gettempdir(), zip_filename), 
            'zip', 
            code_dir
        )
        return zip_path


coding_service = CodingService()
