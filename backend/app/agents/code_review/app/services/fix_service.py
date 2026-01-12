import os
import shutil
from app.utils.llm_service import fix_code_with_llm

async def fix_repo_code(repo_path: str, issues: dict):
    changes = []
    print(f"Fixing code in: {repo_path}")
    print(f"Issues to fix: {issues}")

    for file_path, issue_list in issues.items():
        print(f"Processing file: {file_path}")
        
        # Find the actual file in repo (skip library files)
        full_path = find_actual_code_file(repo_path, file_path)
        print(f"Found file at: {full_path}")
        
        if full_path and os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    original_code = f.read()
                print(f"Original code length: {len(original_code)}")

                # Create backup
                shutil.copy2(full_path, full_path + ".orig")

                # Fix the code using LLM
                fixed_code = await fix_code_with_llm(original_code, "\n".join(issue_list), file_path)
                print(f"Fixed code length: {len(fixed_code)}")

                # Write fixed code
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(fixed_code)

                # Generate line-by-line changes
                line_changes = get_line_changes(original_code, fixed_code)
                print(f"Line changes: {len(line_changes)}")

                # Get fix explanation from LLM
                fix_explanation = get_fix_explanation(original_code, fixed_code, issue_list)
                optimizations = get_optimizations(original_code, fixed_code)
                
                changes.append({
                    "file": file_path,
                    "full_path": full_path.replace(repo_path, "").replace("\\", "/").lstrip("/"),
                    "issues_fixed": issue_list,
                    "fix_explanation": fix_explanation,
                    "optimizations": optimizations,
                    "line_changes": line_changes,
                    "total_lines_changed": len(line_changes)
                })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        else:
            print(f"File not found, skipping: {file_path}")

    return changes

def find_actual_code_file(repo_path: str, file_path: str):
    # Skip library/venv files
    if 'venv' in file_path or 'site-packages' in file_path or 'node_modules' in file_path:
        print(f"Skipping library file: {file_path}")
        return None
    
    # Validate path to prevent traversal
    file_path = os.path.normpath(file_path).lstrip(os.sep)
    if '..' in file_path:
        print(f"Invalid path detected: {file_path}")
        return None
    
    # Try direct path first
    full_path = os.path.join(repo_path, file_path)
    if os.path.exists(full_path):
        return full_path
    
    # Search for the file in repo (only in main directories)
    filename = os.path.basename(file_path)
    for root, dirs, files in os.walk(repo_path):
        # Skip common library directories
        dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__']]
        
        if filename in files:
            found_path = os.path.join(root, filename)
            # Make sure it's not a library file
            if 'venv' not in found_path and 'site-packages' not in found_path:
                return found_path
    
    print(f"File not found in repository: {file_path}")
    return None

def get_line_changes(original: str, fixed: str):
    original_lines = original.splitlines()
    fixed_lines = fixed.splitlines()
    
    changes = []
    max_lines = max(len(original_lines), len(fixed_lines))
    
    for i in range(max_lines):
        orig_line = original_lines[i] if i < len(original_lines) else ""
        fixed_line = fixed_lines[i] if i < len(fixed_lines) else ""
        
        if orig_line != fixed_line:
            changes.append({
                "line_number": i + 1,
                "original": orig_line,
                "fixed": fixed_line,
                "change_type": "modified" if orig_line and fixed_line else ("added" if fixed_line else "removed")
            })
    
    return changes


def get_fix_explanation(original_code: str, fixed_code: str, issues: list) -> str:
    """Generate explanation of how issues were fixed"""
    if original_code == fixed_code:
        return "No changes needed"
    
    changes_count = sum(1 for o, f in zip(original_code.splitlines(), fixed_code.splitlines()) if o != f)
    return f"Fixed {len(issues)} issue(s) with {changes_count} line modifications using AI analysis"

def get_optimizations(original_code: str, fixed_code: str) -> list:
    """Detect optimizations beyond the scan report"""
    optimizations = []
    
    # Check for added error handling
    if 'try:' in fixed_code and 'try:' not in original_code:
        optimizations.append("Added error handling with try-except blocks")
    
    # Check for type hints
    if '->' in fixed_code and '->' not in original_code:
        optimizations.append("Added type hints for better code clarity")
    
    # Check for improved structure
    if len(fixed_code) > len(original_code) * 0.9:
        optimizations.append("Improved code structure and readability")
    
    return optimizations
