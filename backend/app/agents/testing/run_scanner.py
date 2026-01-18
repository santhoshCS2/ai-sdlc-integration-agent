#!/usr/bin/env python3
"""
Quick Folder Structure Generator
Usage: python run_scanner.py
"""

from advanced_scanner import AdvancedFolderScanner
import os

def main():
    print("🚀 Professional Folder Structure Generator")
    print("=" * 50)
    
    # Get user input
    folder_path = input("📁 Enter folder path (press Enter for current): ").strip()
    if not folder_path:
        folder_path = "."
    
    output_name = input("💾 Output filename (default: project_structure.json): ").strip()
    if not output_name:
        output_name = "project_structure.json"
    
    # Validate path
    if not os.path.exists(folder_path):
        print(f"❌ Error: Path '{folder_path}' does not exist!")
        return
    
    # Run scanner
    try:
        scanner = AdvancedFolderScanner()
        result = scanner.generate_structure(folder_path, output_name)
        
        print(f"\n🎉 Success! Structure saved to: {output_name}")
        print(f"📂 Scanned folder: {os.path.abspath(folder_path)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()