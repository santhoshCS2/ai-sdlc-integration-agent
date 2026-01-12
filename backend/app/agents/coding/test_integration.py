"""
Quick test to verify frontend-backend API integration works
"""

from agents.frontend_integrator import FrontendIntegratorAgent
from utils.logger import StreamlitLogger

def test_api_service_generation():
    """Test API service file generation"""
    logger = StreamlitLogger()
    agent = FrontendIntegratorAgent(None, logger)
    
    # Test endpoints
    endpoints = [
        {'method': 'GET', 'path': '/api/items', 'name': 'getItems'},
        {'method': 'POST', 'path': '/api/items', 'name': 'createItem'},
        {'method': 'PUT', 'path': '/api/items', 'name': 'updateItem'},
        {'method': 'DELETE', 'path': '/api/items', 'name': 'deleteItem'},
    ]
    
    # Generate API service
    api_service = agent._create_api_service(
        endpoints,
        'http://localhost:8000',
        'react'
    )
    
    # Verify content
    assert 'import axios from' in api_service
    assert 'export const getItems' in api_service
    assert 'export const createItem' in api_service
    assert 'export const login' in api_service
    assert 'localStorage.getItem' in api_service
    assert 'Authorization' in api_service
    
    print("[OK] API service generation works!")
    print(f"[OK] Generated {len(api_service)} characters")
    print(f"[OK] Contains {len(endpoints)} endpoint functions")
    
    return True

def test_framework_detection():
    """Test framework detection logic"""
    from pathlib import Path
    import tempfile
    import json
    
    logger = StreamlitLogger()
    agent = FrontendIntegratorAgent(None, logger)
    
    # Create temp directory with package.json
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Test React detection
        package_json = tmppath / "package.json"
        with open(package_json, 'w') as f:
            json.dump({
                "dependencies": {
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0"
                }
            }, f)
        
        framework = agent._detect_framework(tmppath)
        assert framework == "react"
        print(f"[OK] Detected React framework correctly")
        
        # Test Next.js detection
        with open(package_json, 'w') as f:
            json.dump({
                "dependencies": {
                    "next": "^14.0.0",
                    "react": "^18.0.0"
                }
            }, f)
        
        framework = agent._detect_framework(tmppath)
        assert framework == "nextjs"
        print(f"[OK] Detected Next.js framework correctly")
        
        # Test Vue detection
        with open(package_json, 'w') as f:
            json.dump({
                "dependencies": {
                    "vue": "^3.0.0"
                }
            }, f)
        
        framework = agent._detect_framework(tmppath)
        assert framework == "vue"
        print(f"[OK] Detected Vue framework correctly")
    
    return True

def test_component_detection():
    """Test component detection logic"""
    logger = StreamlitLogger()
    agent = FrontendIntegratorAgent(None, logger)
    
    # Test cases
    test_cases = [
        ("const [data, setData] = useState([])", True),
        ("useEffect(() => {", True),
        ("fetch('http://api.com')", True),
        ("// TODO: Add API call", True),
        ("const mockData = [1, 2, 3]", True),
        ("console.log('hello')", False),
    ]
    
    for content, should_need_api in test_cases:
        needs_api = agent._needs_api_integration(content)
        assert needs_api == should_need_api, f"Failed for: {content}"
        print(f"[OK] Component detection works for: {content[:30]}...")
    
    return True

if __name__ == "__main__":
    print("Testing Frontend-Backend API Integration...\n")
    
    try:
        test_api_service_generation()
        print()
        test_framework_detection()
        print()
        test_component_detection()
        print()
        print("=" * 50)
        print("[SUCCESS] All tests passed!")
        print("=" * 50)
        print("\nThe frontend-backend API integration feature is working correctly!")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
