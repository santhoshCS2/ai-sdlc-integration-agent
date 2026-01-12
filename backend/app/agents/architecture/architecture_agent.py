import os
import logging
from typing import Optional
from app.agents.architecture.services.github_architecture_service import GitHubArchitectureService
from app.agents.architecture.services.github_pdf_service import GitHubPDFService
from app.core.storage import register_report

logger = logging.getLogger(__name__)

class ArchitectureService:
    def __init__(self):
        self.name = "Architecture Agent"
        self.github_arch_service = GitHubArchitectureService()
        self.github_pdf_service = GitHubPDFService(output_dir="generated_reports")
    
    async def analyze_architecture(self, prd_content: str, github_url: str, github_token: Optional[str] = None) -> str:
        """
        Analyze repository architecture and generate comprehensive documentation.
        
        Args:
            prd_content: Product requirements document content
            github_url: GitHub repository URL
            github_token: Optional GitHub authentication token
            
        Returns:
            Markdown formatted architecture analysis
        """
        try:
            logger.info(f"[Architecture Agent] Analyzing repository: {github_url}")
            
            # Get repository analysis for AI-powered diagrams
            repo_analysis = self.github_arch_service.github_analyzer.analyze_repository(
                github_url, 
                github_token if github_token else None
            )
            
            # Generate comprehensive architecture
            architecture = self.github_arch_service.generate_architecture_from_github(
                github_url=github_url,
                github_token=github_token if github_token else None,
                prd_content=prd_content if prd_content else None
            )
            
            # Format as markdown summary
            markdown_output = f"""# System Architecture Analysis

## Project Overview
- **Application Type**: {architecture.architecture_overview.get('application_type', 'Unknown')}
- **Architecture Pattern**: {architecture.architecture_overview.get('architecture_pattern', 'Unknown')}
- **Complexity Score**: {architecture.architecture_overview.get('complexity_score', 0)}/10
- **Scalability Level**: {architecture.architecture_overview.get('scalability_level', 'Unknown')}

## Technology Stack
- **Languages**: {', '.join(architecture.tech_stack_summary.get('languages', []))}
- **Frameworks**: {', '.join(architecture.tech_stack_summary.get('frameworks', []))}
- **Databases**: {', '.join(architecture.tech_stack_summary.get('databases', []))}

## API Documentation
- **Total Endpoints**: {architecture.api_documentation.get('total_endpoints', 0)}

## Components Analysis
- **Frontend Components**: {architecture.frontend_architecture.get('components', {}).get('total_components', 0)}
- **Backend Services**: {architecture.backend_architecture.get('services', {}).get('total_services', 0)}

## Analysis Summary
{architecture.architecture_overview.get('summary', 'Comprehensive architecture analysis completed.')}
"""
            
            logger.info(f"[Architecture Agent] Analysis completed successfully")
            return markdown_output
            
        except Exception as e:
            logger.error(f"[Architecture Agent] Analysis failed: {str(e)}")
            raise Exception(f"Architecture analysis failed: {str(e)}")
    
    async def generate_architecture_report(self, architecture_content: str, github_url: str) -> Optional[str]:
        """
        Generate a professional PDF report from architecture analysis.
        
        Args:
            architecture_content: Markdown architecture analysis content
            github_url: GitHub repository URL
            
        Returns:
            File ID for the generated PDF report, or None if generation fails
        """
        try:
            logger.info(f"[Architecture Agent] Generating PDF report for {github_url}")
            
            # Re-analyze to get full architecture object for PDF generation
            repo_analysis = self.github_arch_service.github_analyzer.analyze_repository(github_url, None)
            architecture = self.github_arch_service.generate_architecture_from_github(
                github_url=github_url,
                github_token=None,
                prd_content=None
            )
            
            # Generate PDF
            pdf_path = self.github_pdf_service.generate_architecture_pdf(
                architecture=architecture,
                github_url=github_url,
                prd_included=False,
                repo_analysis=repo_analysis,
                prd_content=None
            )
            
            # Register the PDF and return file_id
            import uuid
            file_id = str(uuid.uuid4())
            register_report(file_id, pdf_path)
            
            logger.info(f"[Architecture Agent] PDF report generated: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"[Architecture Agent] PDF generation failed: {str(e)}")
            return None

# Export singleton instance
architecture_service = ArchitectureService()
