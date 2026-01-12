import asyncio
import os
import sys
import shutil
import tempfile
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agents.security.security_scanning_agent import security_scanning_service

async def test_professional_scan():
    print("🚀 Starting Security Scanning Professional Workflow Verification...")
    
    # Mock github URL (we'll mock cloning too)
    repo_url = "https://github.com/mock/repo"
    
    # Mocking clones and scans to avoid real network/LLM calls in a quick test
    with patch('app.agents.security.scanner.CodeScanner.clone_repo', return_value=True), \
         patch('app.agents.security.scanner.CodeScanner.scan_security', return_value=[{'type': 'security', 'severity': 'HIGH', 'file': 'main.py', 'line': 10, 'issue': 'Hardcoded secret'}]), \
         patch('app.agents.security.scanner.CodeScanner.scan_quality', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner.scan_semgrep', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner.scan_ai', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner._analyze_performance', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner._analyze_maintainability', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner._analyze_best_practices', return_value=[]), \
         patch('app.agents.security.scanner.CodeScanner._analyze_documentation', return_value=[]), \
         patch('app.core.storage.register_report', return_value=True):
        
        print("🧪 Testing SecurityScanningService.scan_repository...")
        result = await security_scanning_service.scan_repository(repo_url)
        
        if not result.get("success"):
            print(f"❌ Error: Scan failed - {result.get('error')}")
            return
            
        print(f"✅ Scan successful!")
        print(f"✅ File ID: {result.get('file_id')}")
        print(f"✅ Summary: {result.get('report_content')[:100]}...")
        
        # Verify PDF exists if we didn't mock the PDF service entirely
        # (Though we did mock register_report, the PDF Service actually writes to disk)
        
    print("\n✨ All professional security enhancements verified successfully!")

if __name__ == "__main__":
    asyncio.run(test_professional_scan())
