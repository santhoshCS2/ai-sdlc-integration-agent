"""
FrontendGeneratorAgent - Generates professional React + Vite + Tailwind CSS frontend
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from app.agents.coding.utils.logger import StreamlitLogger

class FrontendGeneratorAgent:
    """Agent that handles frontend code (Neutralized)"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def generate(self, project_spec: Dict[str, Any], frontend_stack: str, project_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Frontend generation disabled by user. Expecting code from GitHub."""
        self.logger.log("ℹ️ Frontend generation is disabled. Using code from GitHub only.")
        return {}
