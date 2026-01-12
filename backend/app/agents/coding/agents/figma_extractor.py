"""
FigmaExtractorAgent - Extracts design tokens, colors, typography from Figma files
"""

from typing import Dict, Any, Optional
from utils.logger import StreamlitLogger

class FigmaExtractorAgent:
    """Agent that extracts design data from Figma"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def extract(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract design data from Figma file"""
        self.logger.log("🎨 Extracting Figma design data...")
        
        figma_file_key = project_config.get("figma_file_key", "")
        skip_figma = project_config.get("skip_figma", False)
        
        if skip_figma or not figma_file_key:
            self.logger.log("⚠️ Skipping Figma extraction - using default design tokens")
            return self._get_default_design_tokens()
        
        try:
            # Try to extract from Figma API
            from utils.figma_client import FigmaClient
            client = FigmaClient()
            
            # Get file data
            file_data = client.get_file(figma_file_key)
            if not file_data:
                self.logger.log("⚠️ Could not fetch Figma file - using default design tokens")
                return self._get_default_design_tokens()
            
            # Extract design tokens
            design_tokens = self._extract_design_tokens(file_data)
            self.logger.log(f"✅ Extracted {len(design_tokens.get('colors', []))} colors and {len(design_tokens.get('typography', []))} typography styles")
            
            return {
                "design_tokens": design_tokens,
                "file_data": file_data,
                "source": "figma"
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log(f"⚠️ Figma extraction failed: {error_msg}")
            
            # Check for specific errors
            if "403" in error_msg or "401" in error_msg:
                self.logger.log("💡 Figma API access issue - check your FIGMA_ACCESS_TOKEN")
            elif "404" in error_msg:
                self.logger.log("💡 Figma file not found - check your file key")
            elif "429" in error_msg:
                self.logger.log("💡 Figma API rate limited - using default tokens")
            
            return self._get_default_design_tokens()
    
    def _extract_design_tokens(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract design tokens from Figma file data"""
        colors = []
        typography = []
        components = []
        frames = []
        
        try:
            # Extract colors from styles
            styles = file_data.get("styles", {})
            for style_id, style in styles.items():
                if style.get("styleType") == "FILL":
                    colors.append({
                        "name": style.get("name", f"Color {len(colors) + 1}"),
                        "value": self._extract_color_value(style),
                        "id": style_id
                    })
                elif style.get("styleType") == "TEXT":
                    typography.append({
                        "name": style.get("name", f"Text {len(typography) + 1}"),
                        "properties": self._extract_text_properties(style),
                        "id": style_id
                    })
            
            # Extract components
            document = file_data.get("document", {})
            if document:
                self._extract_components_recursive(document, components, frames)
            
        except Exception as e:
            self.logger.log(f"⚠️ Error extracting design tokens: {str(e)}")
        
        return {
            "colors": colors,
            "typography": typography,
            "components": components,
            "frames": frames
        }
    
    def _extract_color_value(self, style: Dict[str, Any]) -> str:
        """Extract color value from style"""
        # This is a simplified extraction - real implementation would be more complex
        return "#3B82F6"  # Default blue
    
    def _extract_text_properties(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text properties from style"""
        return {
            "fontSize": "16px",
            "fontFamily": "Inter, sans-serif",
            "fontWeight": "400",
            "lineHeight": "1.5"
        }
    
    def _extract_components_recursive(self, node: Dict[str, Any], components: list, frames: list):
        """Recursively extract components and frames"""
        node_type = node.get("type", "")
        
        if node_type == "COMPONENT":
            components.append({
                "name": node.get("name", "Component"),
                "id": node.get("id", ""),
                "type": node_type
            })
        elif node_type == "FRAME":
            frames.append({
                "name": node.get("name", "Frame"),
                "id": node.get("id", ""),
                "width": node.get("absoluteBoundingBox", {}).get("width", 0),
                "height": node.get("absoluteBoundingBox", {}).get("height", 0)
            })
        
        # Process children
        children = node.get("children", [])
        for child in children:
            self._extract_components_recursive(child, components, frames)
    
    def _get_default_design_tokens(self) -> Dict[str, Any]:
        """Get default design tokens when Figma extraction fails"""
        return {
            "design_tokens": {
                "colors": [
                    {"name": "Primary", "value": "#3B82F6", "id": "primary"},
                    {"name": "Secondary", "value": "#6B7280", "id": "secondary"},
                    {"name": "Success", "value": "#10B981", "id": "success"},
                    {"name": "Warning", "value": "#F59E0B", "id": "warning"},
                    {"name": "Error", "value": "#EF4444", "id": "error"},
                    {"name": "Background", "value": "#FFFFFF", "id": "background"},
                    {"name": "Text", "value": "#1F2937", "id": "text"}
                ],
                "typography": [
                    {"name": "Heading 1", "properties": {"fontSize": "32px", "fontWeight": "700", "fontFamily": "Inter, sans-serif"}},
                    {"name": "Heading 2", "properties": {"fontSize": "24px", "fontWeight": "600", "fontFamily": "Inter, sans-serif"}},
                    {"name": "Heading 3", "properties": {"fontSize": "20px", "fontWeight": "600", "fontFamily": "Inter, sans-serif"}},
                    {"name": "Body", "properties": {"fontSize": "16px", "fontWeight": "400", "fontFamily": "Inter, sans-serif"}},
                    {"name": "Caption", "properties": {"fontSize": "14px", "fontWeight": "400", "fontFamily": "Inter, sans-serif"}}
                ],
                "components": [
                    {"name": "Button", "type": "COMPONENT"},
                    {"name": "Card", "type": "COMPONENT"},
                    {"name": "Input", "type": "COMPONENT"}
                ],
                "frames": [
                    {"name": "Desktop", "width": 1440, "height": 900},
                    {"name": "Mobile", "width": 375, "height": 812}
                ]
            },
            "source": "default"
        }