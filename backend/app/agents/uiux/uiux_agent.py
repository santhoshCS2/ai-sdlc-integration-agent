import io
import pypdf
import logging
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import UploadFile
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

class UIUXService:
    def __init__(self):
        self.name = "UI/UX Design Architect Agent"

    async def _extract_text_from_file(self, file: UploadFile) -> str:
        """Extract text content from uploaded files safely."""
        try:
            filename = getattr(file, "filename", "unknown")
            content = await file.read()
            if not content:
                logger.warning(f"File {filename} is empty.")
                return ""
            
            # Reset pointer for future reads if needed
            await file.seek(0)
                
            text_data = ""
            if filename.lower().endswith(".pdf"):
                try:
                    pdf_file = io.BytesIO(content)
                    reader = pypdf.PdfReader(pdf_file)
                    for i, page in enumerate(reader.pages):
                        extracted = page.extract_text()
                        if extracted:
                            text_data += extracted + "\n"
                    
                    if not text_data.strip():
                        logger.warning(f"PDF {filename} seems to have no extractable text (maybe it's an image?)")
                        # We don't return garbage binary here
                except Exception as pdf_err:
                    logger.error(f"PDF extraction failed for {filename}: {pdf_err}")
            elif filename.lower().endswith((".txt", ".md", ".json", ".yaml", ".yml")):
                text_data = content.decode("utf-8", errors='replace')
            else:
                # Generic fallback for other types
                try:
                    text_data = content.decode("utf-8")
                except:
                    text_data = content.decode("latin-1", errors='ignore')
            
            # Clean up the extracted text - remove non-printable chars but keep basic formatting
            clean_text = "".join(char for char in text_data if char.isprintable() or char in "\n\r\t")
            return clean_text.strip()
        except Exception as e:
            logger.error(f"File reading error: {e}")
            return ""

    async def process_prd(self, query: str, files: Optional[List[UploadFile]] = None) -> str:
        """
        Process PRD content (text and/or files) to generate a high-fidelity Figma AI prompt 
        and a detailed functional UI specification.
        """
        
        # 1. Aggregate PRD Content from all sources
        aggregated_content = []
        
        # Log incoming data for debugging
        logger.info(f"UI/UX Agent: processing query='{query[:50]}...' and {len(files) if files else 0} files")
        
        if query and query.strip() and query != "Process this PRD for SDLC automation":
            aggregated_content.append(f"USER PROVIDED CONTEXT/REQUIREMENTS:\n{query}")
        
        if files:
            for file in files:
                file_text = await self._extract_text_from_file(file)
                if file_text and len(file_text.strip()) > 10:
                    aggregated_content.append(f"DOCUMENT CONTENT ({getattr(file, 'filename', 'unknown')}):\n{file_text}")
                    logger.info(f"Successfully extracted {len(file_text)} chars from file.")
                else:
                    logger.warning(f"Extracted content from {getattr(file, 'filename', 'unknown')} was too short or empty.")
        
        final_prd_input = "\n\n".join(aggregated_content)
        
        # Refined empty content check
        if not final_prd_input.strip():
            # If we only have the placeholder query and no file content was extracted,
            # check if the placeholder itself is all we have.
            is_placeholder = query == "Process this PRD for SDLC automation"
            
            if query and query.strip() and not is_placeholder:
                final_prd_input = query
                logger.info("Using user-provided query as fallback.")
            elif files and len(files) > 0:
                # We had files but couldn't extract text
                log_msg = "Error: The uploaded document(s) could not be read or appear to be empty. Please ensure they contain text or provide requirements manually."
                logger.error(log_msg)
                return log_msg
            else:
                log_msg = "Error: No PRD content detected. Please provide project requirements via text or document upload."
                logger.error(log_msg)
                return log_msg

        logger.info(f"[UI/UX Agent] Analyzing PRD content ({len(final_prd_input)} chars)...")

        # 2. Advanced Multi-Stage System Prompt for Professional Output
        system_prompt = """You are a Senior UI/UX Solution Architect & Design Engineer at a world-class agency.
Your goal is to transform project requirements (PRD) into a comprehensive, high-fidelity 'Figma AI Design Prompt' and a 'Functional UI System Specification'.

Your output MUST be professional, structured, and ready for a design team. Use the following structure:

---
# HIGH-FIDELITY FIGMA DESIGN PROMPT
(This section must be optimized for AI design tools like Figma AI, Midjourney, or DALL-E 3)
[Provide a dense, 200-300 word prompt focusing on: 
 - Visual Style: (e.g., Glassmorphism, Brutalism, Minimalist SaaS, Cyberpunk Dashboard)
 - Color Palette: (Specific HEX codes and gradients)
 - UI Components: (List specific components like 'floating navigation bar with blur effect', 'data-grid with zebra-striping')
 - Interactions: (Hover states, micro-animations)
 - Typography: (Font families and weights)
]

# ARCHITECTURAL DESIGN SPECIFICATION
## 1. User Journey & Core Workflows
[Define the primary paths based on the PRD user stories]

## 2. Information Architecture
[Detailed list of screens and the hierarchical relationship between them]

## 3. Interaction Design Model
[Specific details on how the UI should behave - transitions, loading states, error handling]

## 4. Design-to-Code mapping
[Provide CSS-like variables for colors, spacing, and shadows suggested for the project]

# EXTRACTED BUSINESS LOGIC
[Summarize the critical functional constraints extracted from the PRD that the UI must respect]
---

STRICT REQUIREMENTS:
- NO PLACEHOLDERS. Use actual data from the PRD.
- PROFESSIONAL TONE. Avoid generic descriptions.
- DESIGN DEPTH. Specify shadows, blur amounts, border-radius (e.g., '16px rounded corners'), and opacity levels.
- ROLE-BASED UI. If the PRD mentions multiple roles, define distinct UI states for each.
"""

        user_prompt = f"PRD SOURCE CONTENT:\n{final_prd_input}\n\nTask: Generate the Figma Design Prompt and Architectural Specification."
        
        try:
            design_report = await llm_service.get_response(user_prompt, system_prompt)
            
            # Ensure the report has a professional header
            if not design_report.startswith("#"):
                 design_report = f"# UI/UX ARCHITECTURAL BLUEPRINT\n\n{design_report}"
                 
            return design_report
        except Exception as e:
            logger.error(f"UI/UX Agent LLM prompt failed: {e}")
            return f"Error: The UI/UX engine encountered a technical difficulty. Details: {str(e)}"

uiux_service = UIUXService()