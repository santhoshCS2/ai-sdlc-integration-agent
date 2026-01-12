import os
import logging
import uuid
import json
from typing import Optional, Dict, Any, List
from app.services.llm import llm_service
from app.core.storage import register_report
from .pdf_service import deployment_pdf_service

logger = logging.getLogger(__name__)

class DeploymentService:
    def __init__(self):
        self.name = "Deployment Strategist Agent"

    async def generate_deployment_strategy(self, github_url: str, architecture_context: str, github_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the repository and architecture to generate a deployment strategy.
        """
        logger.info(f"[Deployment Agent] Analyzing deployment for: {github_url}")
        
        # Prepare Railway-specific context
        repo_name = github_url.split('/')[-1].replace('.git', '')
        # Railway's default production URL format
        predicted_url = f"https://{repo_name}-production.up.railway.app"
        
        system_prompt = f"""You are a Senior DevOps & Cloud Infrastructure Architect specializing in Railway.app.
Your task is to analyze the provided GitHub repository and System Architecture to design a Railway-optimized deployment strategy.

You MUST prioritize Railway's 'connected' automation features.
The predicted deployment URL is: {predicted_url}

Output your analysis in JSON format with the following keys:
- architecture_overview (string)
- railway_link_status (string: 'Ready for connection')
- predicted_url (string: '{predicted_url}')
- docker_strategy (string)
- dockerfile_preview (string)
- infrastructure_plan (string: focus on Railway environment)
- cicd_pipeline (string: Railway GitHub triggers)
- deployment_steps (list of objects with 'action' and 'component' keys)
- monitoring_strategy (string)
"""

        user_prompt = f"""GITHUB REPOSITORY: {github_url}
ARCHITECTURE CONTEXT:
{architecture_context}

Task: Generate a comprehensive Railway-focused deployment strategy JSON."""

        try:
            # Get LLM response
            response_text = await llm_service.get_response(user_prompt, system_prompt)
            
            # Clean response if LLM adds markdown triple backticks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            strategy_data = json.loads(response_text)
            
            # Ensure predicted_url is set correctly if LLM changed it
            strategy_data['predicted_url'] = predicted_url
            
            # Generate PDF Report
            file_id = str(uuid.uuid4())
            pdf_path = deployment_pdf_service.generate_report(github_url, strategy_data, file_id)
            register_report(file_id, pdf_path)
            
            # Construct Markdown Report for Chat Output
            report_md = f"### 🚀 Railway Automated Deployment Strategy: {repo_name}\n\n"
            report_md += f"🔗 **Predicted Production URL:** [{predicted_url}]({predicted_url})\n\n"
            report_md += f"#### 🌏 Architecture Overview\n{strategy_data.get('architecture_overview')}\n\n"
            report_md += f"#### 📦 Railway Configuration\n{strategy_data.get('docker_strategy')}\n\n"
            report_md += f"#### ☁️ Resource Plan\n{strategy_data.get('infrastructure_plan')}\n\n"
            report_md += f"#### 🔄 CI/CD Status\nRailway is **connected** via GitHub. Pushes will trigger automatic builds.\n\n"
            report_md += "#### 🛠️ Deployment Steps\n"
            for i, step in enumerate(strategy_data.get('deployment_steps', [])):
                report_md += f"{i+1}. **{step.get('action')}** ({step.get('component')})\n"
            
            return {
                "status": "success",
                "file_id": file_id,
                "report_content": report_md,
                "strategy_data": strategy_data,
                "predicted_url": predicted_url
            }
            
        except Exception as e:
            logger.error(f"[Deployment Agent] Failed to generate strategy: {e}")
            return {
                "status": "error",
                "message": f"Deployment analysis failed: {str(e)}",
                "report_content": "Failed to generate deployment strategy."
            }

deployment_service = DeploymentService()
