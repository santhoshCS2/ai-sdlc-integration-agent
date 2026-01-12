"""
Verify that backend and frontend endpoints match
"""

import re
import json
from pathlib import Path

def extract_backend_endpoints(backend_path):
    """Extract endpoints from backend main.py"""
    main_py = backend_path / "main.py"
    
    if not main_py.exists():
        return []
    
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find FastAPI route decorators
    patterns = [
        r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
        r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
    ]
    
    endpoints = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for method, path in matches:
            endpoints.append({
                'method': method.upper(),
                'path': path
            })
    
    return endpoints

def extract_frontend_endpoints(frontend_path):
    """Extract endpoints from frontend api.js"""
    api_js = frontend_path / "src" / "services" / "api.js"
    
    if not api_js.exists():
        return []
    
    with open(api_js, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find API calls
    patterns = [
        r'api\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
    ]
    
    endpoints = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for method, path in matches:
            # Skip auth endpoints
            if '/auth/' not in path:
                endpoints.append({
                    'method': method.upper(),
                    'path': path
                })
    
    return endpoints

def compare_endpoints(backend_eps, frontend_eps):
    """Compare backend and frontend endpoints"""
    
    print("\n" + "="*60)
    print("ENDPOINT VERIFICATION")
    print("="*60)
    
    print(f"\nBackend Endpoints: {len(backend_eps)}")
    for ep in backend_eps:
        print(f"  {ep['method']:6} {ep['path']}")
    
    print(f"\nFrontend Endpoints: {len(frontend_eps)}")
    for ep in frontend_eps:
        print(f"  {ep['method']:6} {ep['path']}")
    
    # Check matches
    print("\n" + "-"*60)
    print("MATCHING CHECK")
    print("-"*60)
    
    matches = 0
    mismatches = []
    
    for fep in frontend_eps:
        found = False
        for bep in backend_eps:
            if fep['method'] == bep['method'] and fep['path'] == bep['path']:
                found = True
                matches += 1
                print(f"[OK] {fep['method']:6} {fep['path']}")
                break
        
        if not found:
            mismatches.append(fep)
            print(f"[MISSING] {fep['method']:6} {fep['path']} - Not in backend!")
    
    # Check for backend endpoints not in frontend
    for bep in backend_eps:
        found = False
        for fep in frontend_eps:
            if bep['method'] == fep['method'] and bep['path'] == fep['path']:
                found = True
                break
        
        if not found:
            print(f"[EXTRA] {bep['method']:6} {bep['path']} - Backend only")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Matching endpoints: {matches}")
    print(f"Mismatches: {len(mismatches)}")
    
    if len(mismatches) == 0:
        print("\n[SUCCESS] All frontend endpoints match backend!")
        return True
    else:
        print("\n[WARNING] Some endpoints don't match!")
        return False

def verify_project(project_path):
    """Verify a generated project"""
    project_path = Path(project_path)
    
    backend_path = project_path / "backend"
    frontend_path = project_path / "frontend"
    
    if not backend_path.exists():
        print(f"[ERROR] Backend not found: {backend_path}")
        return False
    
    if not frontend_path.exists():
        print(f"[ERROR] Frontend not found: {frontend_path}")
        return False
    
    backend_eps = extract_backend_endpoints(backend_path)
    frontend_eps = extract_frontend_endpoints(frontend_path)
    
    return compare_endpoints(backend_eps, frontend_eps)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        print("Usage: python verify_endpoints.py <project_path>")
        print("\nExample:")
        print("  python verify_endpoints.py C:/path/to/generated/project")
        sys.exit(1)
    
    verify_project(project_path)
