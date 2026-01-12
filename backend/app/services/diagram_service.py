from typing import List, Dict, Optional

class DiagramService:
    def __init__(self):
        pass

    def generate_layered_architecture_mermaid(self, layers: List[str] = None) -> str:
        """
        Generates a standard Layered Architecture diagram in Mermaid.
        """
        if not layers:
            layers = ["Presentation Layer", "Business Logic Layer", "Data Access Layer", "Database Layer"]
        
        mermaid_code = "graph TD\n"
        
        # Create subgraphs for each layer
        for i, layer in enumerate(layers):
            mermaid_code += f"    subgraph {layer.replace(' ', '')}[{layer}]\n"
            mermaid_code += f"        {layer[0]}1[Component]\n"
            mermaid_code += f"    end\n"
            
        # Link layers
        for i in range(len(layers) - 1):
             mermaid_code += f"    {layers[i].replace(' ', '')} --> {layers[i+1].replace(' ', '')}\n"
             
        return mermaid_code

    def generate_system_context_mermaid(self, system_name: str, external_actors: List[str]) -> str:
        """
        Generates a System Context diagram.
        """
        mermaid_code = "graph TD\n"
        mermaid_code += f"    System[{system_name}]\n"
        
        for actor in external_actors:
            mermaid_code += f"    {actor}[{actor}] --> System\n"
            mermaid_code += f"    System --> {actor}\n"
            
        return mermaid_code

diagram_service = DiagramService()
