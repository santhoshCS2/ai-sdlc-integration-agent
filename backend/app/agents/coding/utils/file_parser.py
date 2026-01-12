"""
File Parser for extracting project details from uploaded files
"""

import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
from docx import Document

class FileParser:
    """Parser for extracting project configuration from various file formats"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def parse_file(self, file_content: bytes, file_name: str, file_type: str) -> Dict[str, Any]:
        """Parse uploaded file and extract project details"""
        
        try:
            if file_type == "application/json":
                return self._parse_json(file_content)
            elif file_type == "application/pdf":
                return self._parse_pdf(file_content)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._parse_docx(file_content)
            elif file_type == "text/plain":
                return self._parse_text(file_content.decode('utf-8'))
            else:
                return {"error": f"Unsupported file type: {file_type}"}
        except Exception as e:
            return {"error": f"Error parsing file: {str(e)}"}
    
    def _parse_json(self, file_content: bytes) -> Dict[str, Any]:
        """Parse JSON file for project configuration"""
        try:
            data = json.loads(file_content.decode('utf-8'))
            
            # Direct mapping if JSON has the right structure
            if all(key in data for key in ["project_name", "description", "frontend_stack", "backend_stack"]):
                return {
                    "project_name": data.get("project_name", ""),
                    "description": data.get("description", ""),
                    "frontend_stack": data.get("frontend_stack", "React + Vite"),
                    "backend_stack": data.get("backend_stack", "FastAPI + SQLAlchemy"),
                    "figma_link": data.get("figma_link", "")
                }
            
            # Use LLM to extract from any JSON structure
            return self._extract_with_llm(json.dumps(data, indent=2))
            
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}
    
    def _parse_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """Parse PDF file for project configuration"""
        try:
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return self._extract_with_llm(text)
            
        except Exception as e:
            return {"error": f"Error reading PDF: {str(e)}"}
    
    def _parse_docx(self, file_content: bytes) -> Dict[str, Any]:
        """Parse DOCX file for project configuration"""
        try:
            from io import BytesIO
            doc = Document(BytesIO(file_content))
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._extract_with_llm(text)
            
        except Exception as e:
            return {"error": f"Error reading DOCX: {str(e)}"}
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse plain text file for project configuration"""
        return self._extract_with_llm(text)
    
    def _extract_with_llm(self, content: str) -> Dict[str, Any]:
        """Use LLM to extract project details from any text content"""
        
        prompt = f"""
        Extract project configuration from the following content. Return a JSON object with these exact fields:
        - project_name: A suitable project name (kebab-case, no spaces)
        - frontend_stack: One of ["React + Vite", "Next.js 14", "Vue 3 + Vite", "SvelteKit"] (extract if mentioned, otherwise use "React + Vite")
        - backend_stack: One of ["FastAPI + SQLAlchemy", "Django", "Node.js/Express + Prisma", "Supabase", "Firebase"] (extract if mentioned, otherwise use "FastAPI + SQLAlchemy")
        - figma_link: Any Figma URL or file key found (empty string if none)
        - description: ALL remaining content after extracting the above fields. This should be the full project description, requirements, features, and any other details. Include everything that is not project_name, frontend_stack, backend_stack, or figma_link.
        
        IMPORTANT: The description field should contain ALL the remaining content from the original text after extracting project_name, frontend_stack, backend_stack, and figma_link. Do not summarize - include the full remaining content.
        
        Content to analyze:
        {content}
        
        Return only valid JSON, no other text:
        """
        
        try:
            response = self.llm.invoke(prompt)
            result_text = response.content.strip()
            
            # Clean up response to get just JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            parsed = json.loads(result_text)
            
            # Validate required fields
            required_fields = ["project_name", "description", "frontend_stack", "backend_stack", "figma_link"]
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = ""
            
            # If description is empty or too short, use the original content minus extracted fields
            if not parsed.get("description") or len(parsed.get("description", "")) < 50:
                parsed["description"] = self._extract_remaining_as_description(content, parsed)
            
            return parsed
            
        except Exception as e:
            # Fallback: try to extract with regex
            return self._extract_with_regex(content)
    
    def _extract_remaining_as_description(self, original_content: str, extracted: Dict[str, Any]) -> str:
        """Extract remaining content as description after removing extracted fields"""
        content = original_content
        
        # Remove project name if found
        if extracted.get("project_name"):
            project_name_variations = [
                extracted["project_name"],
                extracted["project_name"].replace("-", " "),
                extracted["project_name"].replace("-", "_"),
            ]
            for variant in project_name_variations:
                content = re.sub(re.escape(variant), "", content, flags=re.IGNORECASE)
        
        # Remove frontend stack if found
        if extracted.get("frontend_stack"):
            content = re.sub(re.escape(extracted["frontend_stack"]), "", content, flags=re.IGNORECASE)
        
        # Remove backend stack if found
        if extracted.get("backend_stack"):
            content = re.sub(re.escape(extracted["backend_stack"]), "", content, flags=re.IGNORECASE)
        
        # Remove Figma link if found
        if extracted.get("figma_link"):
            content = re.sub(re.escape(extracted["figma_link"]), "", content, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # If still empty, return original content
        if not content or len(content) < 10:
            return original_content.strip()
        
        return content
    
    def _extract_with_regex(self, content: str) -> Dict[str, Any]:
        """Fallback regex extraction"""
        
        # Store original content for description fallback
        original_content = content
        
        # Common patterns
        figma_pattern = r'(?:https?://)?(?:www\.)?figma\.com/(?:file|design|community/file)/([a-zA-Z0-9_-]+)'
        
        # Frontend stack patterns
        frontend_patterns = {
            r'(?i)(?:react\s*\+\s*vite|react.*vite)': "React + Vite",
            r'(?i)(?:next\.?js\s*14|nextjs\s*14)': "Next.js 14",
            r'(?i)(?:vue\s*3\s*\+\s*vite|vue.*vite)': "Vue 3 + Vite",
            r'(?i)sveltekit': "SvelteKit"
        }
        
        # Backend stack patterns
        backend_patterns = {
            r'(?i)(?:fastapi\s*\+\s*sqlalchemy|fastapi.*sqlalchemy)': "FastAPI + SQLAlchemy",
            r'(?i)django': "Django",
            r'(?i)(?:node\.?js.*express.*prisma|express.*prisma)': "Node.js/Express + Prisma",
            r'(?i)supabase': "Supabase",
            r'(?i)firebase': "Firebase"
        }
        
        result = {
            "project_name": "",
            "description": "",
            "frontend_stack": "React + Vite",
            "backend_stack": "FastAPI + SQLAlchemy",
            "figma_link": ""
        }
        
        # Extract Figma link
        figma_match = re.search(figma_pattern, content)
        if figma_match:
            result["figma_link"] = figma_match.group(0)
            # Remove from content for description
            content = re.sub(figma_pattern, "", content, flags=re.IGNORECASE)
        
        # Extract frontend stack
        for pattern, stack in frontend_patterns.items():
            if re.search(pattern, content):
                result["frontend_stack"] = stack
                # Remove from content for description
                content = re.sub(pattern, "", content, flags=re.IGNORECASE)
                break
        
        # Extract backend stack
        for pattern, stack in backend_patterns.items():
            if re.search(pattern, content):
                result["backend_stack"] = stack
                # Remove from content for description
                content = re.sub(pattern, "", content, flags=re.IGNORECASE)
                break
        
        # Extract project name (look for title-like patterns)
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 5 and len(line) < 50 and not line.startswith('#'):
                project_name = re.sub(r'[^a-zA-Z0-9\s-]', '', line).strip().lower().replace(' ', '-')
                if project_name:
                    result["project_name"] = project_name
                    # Remove from content for description
                    content = re.sub(re.escape(line), "", content, flags=re.IGNORECASE)
                    break
        
        # Use remaining content as description
        content = re.sub(r'\s+', ' ', content).strip()
        if content and len(content) > 10:
            result["description"] = content[:200000]  # Limit to 200000 chars
        else:
            # If nothing left, use original content
            result["description"] = original_content[:200000]
        
        return result