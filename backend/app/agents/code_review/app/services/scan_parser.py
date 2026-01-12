import json
import re
import csv
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyPDF2 not installed. PDF support disabled.")

def parse_scan_report(text: Optional[str], file_bytes: Optional[bytes] = None) -> Dict[str, List[str]]:
    print(f"Parsing scan report: {text[:200] if text else 'binary data'}...")
    
    # Try PDF if binary data provided
    if file_bytes and PDF_SUPPORT:
        result = parse_pdf(file_bytes)
        if result: return result
    
    # Try JSON first
    result = parse_json(text)
    if result: return result
    
    # Try XML
    result = parse_xml(text)
    if result: return result
    
    # Try CSV
    result = parse_csv(text)
    if result: return result
    
    # Try plain text
    result = parse_text(text)
    if result: return result
    
    print("No valid format detected, using default")
    return {"main.py": ["Code review needed"]}

def parse_pdf(file_bytes: bytes) -> Optional[Dict[str, List[str]]]:
    if not PDF_SUPPORT:
        return None
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        print(f"PDF extracted: {len(text)} chars")
        
        # Try parsing extracted text as other formats
        result = parse_json(text) or parse_xml(text) or parse_csv(text) or parse_text(text)
        return result if result else None
    except Exception as e:
        return None

def parse_json(text: Optional[str]) -> Optional[Dict[str, List[str]]]:
    if not text:
        return None
    try:
        data = json.loads(text)
        issues = {}
        findings = data.get("findings", data.get("issues", data.get("results", [])))
        
        for f in findings:
            file = f.get("file") or f.get("file_path") or f.get("path") or f.get("location") or "main.py"
            
            # Try multiple fields for issue description
            msg = (f.get("issue") or f.get("message") or f.get("issue_description") or 
                   f.get("description") or f.get("title"))
            
            # Add line number and severity if available
            line = f.get("line")
            severity = f.get("severity")
            
            if msg:
                if line:
                    msg = f"Line {line}: {msg}"
                if severity:
                    msg = f"[{severity}] {msg}"
            else:
                # If no message, try to extract from suggested_fix or original_code
                suggested = f.get("suggested_fix", "")
                original = f.get("original_code", "")
                if suggested and original:
                    msg = f"Code improvement: {original[:50]}... → {suggested[:50]}..."
                else:
                    msg = "Code quality improvement needed"
            
            if file not in issues:
                issues[file] = []
            issues[file].append(msg)
        
        print(f"JSON parsed: {len(issues)} files")
        return issues if issues else None
    except Exception:
        return None

def parse_xml(text: Optional[str]) -> Optional[Dict[str, List[str]]]:
    if not text:
        return None
    try:
        root = ET.fromstring(text)
        issues = {}
        
        for item in root.iter():
            if item.tag in ['issue', 'finding', 'error', 'warning', 'violation']:
                file = item.get('file') or item.findtext('file') or item.findtext('path') or "main.py"
                msg = item.get('message') or item.findtext('message') or item.findtext('description') or "Code issue"
                
                if file not in issues:
                    issues[file] = []
                issues[file].append(msg)
        
        print(f"XML parsed: {len(issues)} files")
        return issues if issues else None
    except Exception:
        return None

def parse_csv(text: Optional[str]) -> Optional[Dict[str, List[str]]]:
    if not text:
        return None
    try:
        reader = csv.DictReader(StringIO(text))
        issues = {}
        
        for row in reader:
            file = row.get('file') or row.get('path') or row.get('filename') or row.get('File') or "main.py"
            msg = row.get('message') or row.get('issue') or row.get('description') or row.get('Message') or "Code issue"
            
            if file not in issues:
                issues[file] = []
            issues[file].append(msg)
        
        print(f"CSV parsed: {len(issues)} files")
        return issues if issues else None
    except Exception:
        return None

def parse_text(text: Optional[str]) -> Optional[Dict[str, List[str]]]:
    if not text:
        return None
    try:
        issues = {}
        lines = text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Pattern: file.py: issue description
            match = re.match(r'([^:]+\.\w+)\s*[:|]\s*(.+)', line)
            if match:
                file, msg = match.groups()
                file = file.strip()
                msg = msg.strip()
            else:
                # Pattern: "file.py" or just text
                file_match = re.search(r'([\w/\\.-]+\.\w+)', line)
                file = file_match.group(1) if file_match else "main.py"
                msg = line.strip()
            
            if file not in issues:
                issues[file] = []
            issues[file].append(msg)
        
        print(f"Text parsed: {len(issues)} files")
        return issues if issues else None
    except Exception:
        return None