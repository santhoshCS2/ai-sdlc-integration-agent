import os
import json
from datetime import datetime

class FolderStructureGenerator:
    def __init__(self, root_path=".", output_file="folder_structure.json", 
                 ignore_dirs=None, text_extensions=None, max_file_size=500000):
        self.root_path = os.path.abspath(root_path)
        self.output_file = output_file
        self.ignore_dirs = ignore_dirs or {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        self.text_extensions = text_extensions or {'.py', '.js', '.html', '.css', '.json', '.md', '.txt', '.xml', '.yml', '.yaml'}
        self.max_file_size = max_file_size
    
    def is_text_file(self, file_path):
        return any(file_path.lower().endswith(ext) for ext in self.text_extensions)
    
    def get_file_content(self, file_path):
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return "[File too large]"
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return "[Cannot read file]"
    
    def scan_item(self, item_path, relative_path=""):
        item_name = os.path.basename(item_path)
        
        if os.path.isdir(item_path):
            if item_name in self.ignore_dirs:
                return None
            
            folder_data = {
                "name": item_name,
                "type": "directory",
                "path": relative_path,
                "children": []
            }
            
            try:
                items = os.listdir(item_path)
                items.sort()
                
                for item in items:
                    full_path = os.path.join(item_path, item)
                    child_relative = os.path.join(relative_path, item) if relative_path else item
                    
                    child_data = self.scan_item(full_path, child_relative)
                    if child_data:
                        folder_data["children"].append(child_data)
            except:
                folder_data["error"] = "Access denied"
            
            return folder_data
        
        else:
            try:
                file_size = os.path.getsize(item_path)
                file_data = {
                    "name": item_name,
                    "type": "file",
                    "path": relative_path,
                    "size": file_size,
                    "extension": os.path.splitext(item_name)[1]
                }
                
                if self.is_text_file(item_name):
                    file_data["content"] = self.get_file_content(item_path)
                
                return file_data
            except:
                return {"name": item_name, "type": "file", "error": "Cannot access"}
    
    def generate(self):
        print(f"Scanning: {self.root_path}")
        
        structure = {
            "metadata": {
                "root_path": self.root_path,
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "generator": "Professional Folder Scanner"
            },
            "structure": self.scan_item(self.root_path)
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated: {self.output_file}")
        return structure

def main():
    folder = input("Folder path (Enter for current): ").strip() or "."
    output = input("Output file (Enter for default): ").strip() or "structure.json"
    
    if not os.path.exists(folder):
        print("❌ Folder not found!")
        return
    
    generator = FolderStructureGenerator(folder, output)
    generator.generate()

if __name__ == "__main__":
    main()