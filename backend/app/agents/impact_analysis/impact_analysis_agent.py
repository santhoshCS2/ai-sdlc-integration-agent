import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging

from app.services.llm import llm_service
from app.core.storage import register_report
from app.agents.impact_analysis.services.impact_pdf_service import impact_pdf_service

logger = logging.getLogger(__name__)

class ImpactAnalysisService:
    def __init__(self):
        self.name = "Business & Technical Impact Agent"

    async def analyze_impact(self, prd_content: str, architecture_content: str, github_url: Optional[str] = None) -> Dict[str, str]:
        """
        Analyze technical and business impact based on PRD and architecture.
        """
        try:
            logger.info(f"[Impact Analysis Agent] Starting impact analysis...")
            
            # Create comprehensive system prompt for impact analysis
            system_prompt = """You are a Senior Business & Technical Impact Analyst with expertise in:
- Business Impact Assessment (ROI, Cost-Benefit Analysis)
- Technical Risk Assessment (Scalability, Security, Performance)
- Resource Planning & Timeline Estimation
- Stakeholder Impact Analysis

Your task is to provide a professional impact analysis report.
"""

            user_prompt = f"""
PROJECT CONTEXT:
{prd_content[:2000]}

SYSTEM ARCHITECTURE:
{architecture_content[:2000]}

GITHUB REPOSITORY: {github_url or 'Not provided'}

Please provide a comprehensive impact analysis covering all business and technical aspects.
"""

            # Get LLM response
            impact_report = await llm_service.get_response(user_prompt, system_prompt)
            
            # Ensure the report has a professional header
            if not impact_report.startswith("#"):
                impact_report = f"# COMPREHENSIVE IMPACT ANALYSIS REPORT\n\n{impact_report}"
            
            # Generate professional PDF report
            file_id = str(uuid.uuid4())
            pdf_path = impact_pdf_service.generate_report(github_url, impact_report, file_id)
            
            # Register the report for download (pdf_path is already absolute from service)
            register_report(file_id, pdf_path)
            
            logger.info(f"[Impact Analysis Agent] Impact analysis completed successfully: {file_id}")
            
            return {
                "report_content": impact_report,
                "file_id": file_id
            }
            
        except Exception as e:
            logger.error(f"Impact Analysis Agent error: {e}")
            return {
                "report_content": f"Error: Impact analysis failed - {str(e)}",
                "file_id": None
            }

# Create service instance
impact_analysis_service = ImpactAnalysisService()