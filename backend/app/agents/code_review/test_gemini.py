import requests
import json

test_scan_report = {
    "findings": [
        {
            "file": "main.py",
            "message": "Missing parentheses in print statement"
        },
        {
            "file": "main.py",
            "message": "Add error handling for division by zero"
        }
    ]
}

def test_gemini():
    url = "http://localhost:8000/review"
    repo_url = "https://github.com/leeladri03/multimodal_app"
    
    data = {'repo_url': repo_url}
    files = {'scan_report': ('report.json', json.dumps(test_scan_report), 'application/json')}
    
    try:
        print("Testing with Gemini API...")
        response = requests.post(url, data=data, files=files, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Fixed Repo: {result['fixed_repo']}")
            
            for change in result['changes']:
                print(f"\nFile: {change['file']}")
                print(f"Issues Fixed: {change['issues_fixed']}")
                print(f"Lines Changed: {change['total_lines_changed']}")
                
                for line_change in change['line_changes'][:5]:
                    print(f"  Line {line_change['line_number']} ({line_change['change_type']}):")
                    if line_change['original']:
                        print(f"    - {line_change['original']}")
                    if line_change['fixed']:
                        print(f"    + {line_change['fixed']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()