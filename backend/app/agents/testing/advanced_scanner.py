import os
import json
import mimetypes
from datetime import datetime
from pathlib import Path
import argparse
import hashlib

class AdvancedFolderScanner:
    def __init__(self, config_file="config.json"):
        self.load_config(config_file)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.ignore_dirs = set(config.get("ignore_directories", []))
            self.ignore_files = set(config.get("ignore_files", []))
            self.text_extensions = set(config.get("text_extensions", []))
            self.max_size_mb = config.get("max_file_size_mb", 1)
            self.include_content = config.get("include_content", True)
            self.include_metadata = config.get("include_metadata", True)
        except FileNotFoundError:
            self.set_defaults()
    
    def set_defaults(self):
        """Set default configuration"""
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', '.vscode'}
        self.ignore_files = {'.gitignore', '.DS_Store'}
        self.text_extensions = {'.py', '.js', '.html', '.css', '.json', '.md', '.txt'}
        self.max_size_mb = 1
        self.include_content = True
        self.include_metadata = True
    
    def get_file_hash(self, file_path):
        """Generate MD5 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def analyze_file(self, file_path, root_path):
        """Comprehensive file analysis"""
        try:
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(root_path))
            
            file_info = {
                "name": file_path.name,
                "path": relative_path,
                "type": "file",
                "size": stat.st_size,
                "extension": file_path.suffix.lower(),
                "is_text": file_path.suffix.lower() in self.text_extensions
            }
            
            if self.include_metadata:
                file_info.update({
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "hash": self.get_file_hash(file_path)
                })
            
            # Include file content for text files
            if (self.include_content and file_info["is_text"] and 
                stat.st_size < self.max_size_mb * 1024 * 1024):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_info["content"] = content
                        file_info["lines"] = len(content.splitlines())
                except UnicodeDecodeError:
                    file_info["content"] = "[Binary content]"
            
            return file_info
            
        except Exception as e:
            return {"name": file_path.name, "error": str(e)}
    
    def scan_folder(self, folder_path, root_path):
        """Recursively scan folder structure"""
        folder_info = {
            "name": folder_path.name,
            "path": str(folder_path.relative_to(root_path)),
            "type": "directory",
            "children": []
        }
        
        try:
            items = list(folder_path.iterdir())
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.') and item.name in self.ignore_files:
                    continue
                
                if item.is_dir():
                    if item.name not in self.ignore_dirs:
                        folder_info["children"].append(self.scan_folder(item, root_path))
                else:
                    if not any(item.name.endswith(pattern.replace('*', '')) 
                             for pattern in self.ignore_files if '*' in pattern):
                        folder_info["children"].append(self.analyze_file(item, root_path))
            
            # Add folder statistics
            if self.include_metadata:
                folder_info["stats"] = {
                    "total_items": len(folder_info["children"]),
                    "files": sum(1 for child in folder_info["children"] if child["type"] == "file"),
                    "directories": sum(1 for child in folder_info["children"] if child["type"] == "directory")
                }
                
        except PermissionError:
            folder_info["error"] = "Access denied"
        
        return folder_info
    
    def generate_structure(self, root_path, output_file):
        """Generate complete folder structure"""
        root_path = Path(root_path).resolve()
        print(f"🔍 Scanning: {root_path}")
        
        structure = {
            "metadata": {
                "root_path": str(root_path),
                "scan_date": datetime.now().isoformat(),
                "generator": "Advanced Folder Scanner v2.0",
                "config": {
                    "include_content": self.include_content,
                    "max_file_size_mb": self.max_size_mb,
                    "ignored_dirs": list(self.ignore_dirs),
                    "text_extensions": list(self.text_extensions)
                }
            },
            "structure": self.scan_folder(root_path, root_path)
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated: {output_file}")
        self.print_summary(structure)
        return structure
    
    def print_summary(self, structure):
        """Print scan summary"""
        def count_items(node):
            if node["type"] == "file":
                return 1, 0
            files, dirs = 0, 1
            for child in node.get("children", []):
                f, d = count_items(child)
                files += f
                dirs += d
            return files, dirs
        
        total_files, total_dirs = count_items(structure["structure"])
        print(f"📊 Summary: {total_files} files, {total_dirs} directories")

def main():
    parser = argparse.ArgumentParser(description="Professional Folder Structure Generator")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument("-o", "--output", default="structure.json", help="Output file")
    parser.add_argument("-c", "--config", default="config.json", help="Config file")
    
    args = parser.parse_args()
    
    scanner = AdvancedFolderScanner(args.config)
    scanner.generate_structure(args.path, args.output)

if __name__ == "__main__":
    main()