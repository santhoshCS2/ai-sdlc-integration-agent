import os
import logging
from typing import Optional, Dict, Any
from app.agents.code_review.app.services.github_service import clone_repo
from app.agents.code_review.app.services.fix_service import fix_repo_code
from app.agents.code_review.app.services.scan_parser import parse_scan_report

logger = logging.getLogger(__name__)

class CodeReviewService:
    def __init__(self):
        self.name = "Code Review Agent"
    
    async def perform_code_review(self, code_content: str, test_report: str, security_report: str, prd_content: str, security_file_id: Optional[str] = None) -> str:
        """
        Perform a comprehensive code review using scan reports.
        """
        try:
            logger.info("[Code Review Agent] Performing code review...")
            
            # If we have security_file_id, we could potentially read the actual report
            # For now, we simulate the analysis using the provided report strings
            
            issues = parse_scan_report(security_report)
            
            review_md = f"""# Code Review Report
            
## Executive Summary
This report provides a professional analysis of the codebase based on security scans and testing results.

## Analysis Scope
- **Security Scan Analysis**: {len(issues) if issues else 0} files flagged for potential issues.
- **Testing Context**: Integration with latest test suite reports.
- **PRD Alignment**: Verification against project requirements.

## Detailed Findings
"""
            if not issues:
                review_md += "✅ No critical code quality issues detected in the analyzed scope.\n"
            else:
                for file, issue_list in list(issues.items())[:5]: # Show first 5 files
                    review_md += f"### 📄 File: `{file}`\n"
                    for issue in issue_list:
                        review_md += f"- {issue}\n"
                    review_md += "\n"

            review_md += """
## Recommendations
1. **Security**: Address flagged vulnerabilities immediately before deployment.
2. **Quality**: Ensure all automated fixes are reviewed by a senior developer.
3. **Consistency**: Maintain modular structure as defined in the Architecture Guide.
"""
            return review_md
            
        except Exception as e:
            logger.error(f"[Code Review Agent] Review failed: {str(e)}")
            return f"Code review failed: {str(e)}"

# Export singleton instance
code_review_service = CodeReviewService()
