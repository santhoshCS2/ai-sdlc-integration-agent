import os
import json
from datetime import datetime

def scan_folder(path):
    """Simple folder scanner that always works"""
    result = {
        "name": os.path.basename(path) or path,
        "type": "directory",
        "children": []
    }
    
    try:
        items = os.listdir(path)
        items.sort()
        
        for item in items:
            if item.startswith('.'):
                continue
                
            full_path = os.path.join(path, item)
            
            if os.path.isdir(full_path):
                if item not in ['__pycache__', 'node_modules', '.git']:
                    result["children"].append(scan_folder(full_path))
            else:
                file_info = {
                    "name": item,
                    "type": "file",
                    "size": 0
                }
                
                try:
                    file_info["size"] = os.path.getsize(full_path)
                    
                    # Read text files
                    if any(item.endswith(ext) for ext in ['.py', '.js', '.html', '.css', '.json', '.md', '.txt']):
                        if file_info["size"] < 100000:  # < 100KB
                            try:
                                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    file_info["content"] = f.read()
                            except:
                                pass
                except:
                    pass
                
                result["children"].append(file_info)
    except:
        result["error"] = "Cannot access"
    
    return result

def generate_structure(folder_path=".", output_file="structure.json"):
    """Generate folder structure JSON"""
    print(f"Scanning: {os.path.abspath(folder_path)}")
    
    data = {
        "scan_info": {
            "path": os.path.abspath(folder_path),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "structure": scan_folder(folder_path)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done: {output_file}")

if __name__ == "__main__":
    folder = input("Folder (Enter for current): ").strip() or "."
    output = input("Output file (Enter for structure.json): ").strip() or "structure.json"
    generate_structure(folder, output)