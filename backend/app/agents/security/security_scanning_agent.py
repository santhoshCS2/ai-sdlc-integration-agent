import os
import logging
import uuid
import json
from typing import Optional, Dict, Any, List
from app.agents.security.scanner import CodeScanner
from app.core.storage import register_report
from app.agents.security.report_generator import generate_report_for_scan
from app.agents.security.pdf_service import security_pdf_service

logger = logging.getLogger(__name__)

class SecurityScanningService:
    def __init__(self):
        self.name = "Security Scanning Agent"
        # The scanner logic expects instances to be created per scan in many cases,
        # but here we'll manage the lifecycle within the service method.
    
    async def scan_repository(self, github_url: str, testing_file_id: Optional[str] = None, github_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan a repository for security vulnerabilities and code quality issues.
        """
        scanner = CodeScanner(deep_scan=True)
        try:
            logger.info(f"[Security Agent] Starting comprehensive scan for: {github_url}")
            
            if not scanner.clone_repo(github_url):
                return {
                    "success": False,
                    "error": "Failed to clone repository",
                    "report_content": "Security scan failed: Could not clone repository."
                }
            
            # 1. Run all scan engines
            logger.info("[Security Agent] Running SAST (Bandit/Pylint/Semgrep)...")
            security_issues = scanner.scan_security()
            quality_issues = scanner.scan_quality()
            semgrep_issues = scanner.scan_semgrep()
            
            logger.info("[Security Agent] Running AI Analysis...")
            ai_issues = scanner.scan_ai()
            
            logger.info("[Security Agent] Running Advanced Quality Analysis...")
            perf_issues = scanner._analyze_performance()
            maint_issues = scanner._analyze_maintainability()
            bp_issues = scanner._analyze_best_practices()
            doc_issues = scanner._analyze_documentation()
            
            # Combine all findings
            all_issues = (security_issues + quality_issues + semgrep_issues + ai_issues + 
                         perf_issues + maint_issues + bp_issues + doc_issues)
            
            # 2. Generate Comprehensive Report Data
            logger.info("[Security Agent] Generating dynamic report data...")
            scan_data = {
                'job_id': str(uuid.uuid4()),
                'repo_url': github_url,
                'issues': all_issues,
                'unit_test_report': {} # Could be integrated if testing_file_id provided
            }
            comprehensive_report = generate_report_for_scan(scan_data)
            
            # Add raw issues for PDF generator
            comprehensive_report['raw_data']['issues'] = all_issues
            
            # 3. Generate Professional PDF
            logger.info("[Security Agent] Generating professional PDF report...")
            file_id = str(uuid.uuid4())
            pdf_path = security_pdf_service.generate_report(github_url, comprehensive_report, file_id)
            
            # Register for download
            register_report(file_id, pdf_path)
            
            # 4. Success Response
            return {
                "success": True,
                "report_content": comprehensive_report['executive_summary'],
                "file_id": file_id,
                "statistics": {
                    "security_issues": len([i for i in all_issues if i.get('type') == 'security']),
                    "quality_issues": len([i for i in all_issues if i.get('type') == 'quality']),
                    "total_issues": len(all_issues)
                },
                "comprehensive_report": comprehensive_report
            }
            
        except Exception as e:
            logger.error(f"[Security Agent] Scan failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "report_content": f"Security scan failed: {str(e)}"
            }
        finally:
            scanner.cleanup()

# Export singleton instance
security_scanning_service = SecurityScanningService()
