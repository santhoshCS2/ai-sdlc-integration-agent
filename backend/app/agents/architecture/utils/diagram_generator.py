import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from typing import List, Dict, Tuple
import io
import base64

class ProfessionalDiagramGenerator:
    """Generate clean, professional architecture diagrams"""
    
    def __init__(self):
        plt.style.use('default')
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'accent': '#F18F01',
            'success': '#C73E1D',
            'light': '#F5F5F5',
            'dark': '#2C3E50',
            'text': '#34495E'
        }
    
    def generate_system_architecture(self, repo_data: dict, api_endpoints: List[dict] = None) -> str:
        """Generate dynamic system architecture diagram with real data"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Extract real data
        frontend_tech = repo_data.get('frontend_tech', [])
        backend_tech = repo_data.get('backend_tech', [])
        database_tech = repo_data.get('database_tech', [])
        languages = list(repo_data.get('languages', {}).keys())
        file_count = repo_data.get('file_count', 0)
        components_count = repo_data.get('components_total', 0)
        api_count = len(api_endpoints) if api_endpoints else 0
        
        # Dynamic title based on detected tech
        main_tech = frontend_tech[0] if frontend_tech else (backend_tech[0] if backend_tech else 'Web')
        ax.text(6, 9.5, f'{main_tech} System Architecture', fontsize=18, fontweight='bold', 
                ha='center', color=self.colors['dark'])
        
        # Client Layer - dynamic based on frontend
        client_box = FancyBboxPatch((1, 8), 10, 0.8, boxstyle="round,pad=0.1",
                                   facecolor=self.colors['primary'], edgecolor='white', linewidth=2)
        ax.add_patch(client_box)
        ax.text(6, 8.4, 'Client Layer', fontsize=14, fontweight='bold', ha='center', color='white')
        
        client_types = []
        if 'React' in str(frontend_tech) or 'Vue' in str(frontend_tech):
            client_types.append('SPA Browser')
        if 'Next.js' in str(frontend_tech):
            client_types.append('SSR Web App')
        if not client_types:
            client_types = ['Web Browser', 'Mobile App']
        
        ax.text(6, 8.1, ' • '.join(client_types), fontsize=10, ha='center', color='white')
        
        # Frontend Layer - real tech stack
        if frontend_tech or components_count > 0:
            frontend_box = FancyBboxPatch((1, 6.5), 10, 0.8, boxstyle="round,pad=0.1",
                                         facecolor=self.colors['secondary'], edgecolor='white', linewidth=2)
            ax.add_patch(frontend_box)
            ax.text(6, 6.9, 'Frontend Layer', fontsize=14, fontweight='bold', ha='center', color='white')
            
            frontend_details = []
            if frontend_tech:
                frontend_details.extend(frontend_tech[:3])
            if components_count > 0:
                frontend_details.append(f'{components_count} Components')
            if languages:
                frontend_details.append(f'{len(languages)} Languages')
            
            ax.text(6, 6.6, ' • '.join(frontend_details), fontsize=10, ha='center', color='white')
            frontend_y = 6.5
        else:
            frontend_y = 8
        
        # Backend Layer - real backend tech
        backend_y = frontend_y - 1.5
        if backend_tech or api_count > 0:
            backend_box = FancyBboxPatch((1, backend_y), 10, 0.8, boxstyle="round,pad=0.1",
                                        facecolor=self.colors['accent'], edgecolor='white', linewidth=2)
            ax.add_patch(backend_box)
            ax.text(6, backend_y + 0.4, 'Backend Layer', fontsize=14, fontweight='bold', ha='center', color='white')
            
            backend_details = []
            if backend_tech:
                backend_details.extend(backend_tech[:3])
            if api_count > 0:
                backend_details.append(f'{api_count} APIs')
            if file_count > 0:
                backend_details.append(f'{file_count} Files')
            
            if not backend_details:
                backend_details = ['API Server', 'Business Logic']
            
            ax.text(6, backend_y + 0.1, ' • '.join(backend_details), fontsize=10, ha='center', color='white')
        
        # Database Layer - real database tech
        db_y = backend_y - 1.5
        db_box = FancyBboxPatch((1, db_y), 10, 0.8, boxstyle="round,pad=0.1",
                               facecolor=self.colors['success'], edgecolor='white', linewidth=2)
        ax.add_patch(db_box)
        ax.text(6, db_y + 0.4, 'Database Layer', fontsize=14, fontweight='bold', ha='center', color='white')
        
        db_details = []
        if database_tech:
            db_details.extend(database_tech[:3])
        else:
            db_details = ['PostgreSQL', 'Data Storage']
        
        ax.text(6, db_y + 0.1, ' • '.join(db_details), fontsize=10, ha='center', color='white')
        
        # Dynamic arrows based on actual layers
        arrow_props = dict(arrowstyle='->', lw=3, color=self.colors['dark'])
        
        if frontend_tech:
            ax.annotate('', xy=(6, frontend_y), xytext=(6, 7.8), arrowprops=arrow_props)
            ax.text(6.5, (frontend_y + 7.8) / 2, 'HTTP/HTTPS', fontsize=9, color=self.colors['text'], style='italic')
            
            ax.annotate('', xy=(6, backend_y), xytext=(6, frontend_y - 0.2), arrowprops=arrow_props)
            ax.text(6.5, (backend_y + frontend_y) / 2, f'REST API ({api_count} endpoints)', fontsize=9, color=self.colors['text'], style='italic')
        else:
            ax.annotate('', xy=(6, backend_y), xytext=(6, 7.8), arrowprops=arrow_props)
            ax.text(6.5, (backend_y + 7.8) / 2, 'Direct API', fontsize=9, color=self.colors['text'], style='italic')
        
        ax.annotate('', xy=(6, db_y), xytext=(6, backend_y - 0.2), arrowprops=arrow_props)
        db_protocol = 'SQL' if any('SQL' in str(db) for db in database_tech) else 'Database'
        ax.text(6.5, (db_y + backend_y) / 2, db_protocol, fontsize=9, color=self.colors['text'], style='italic')
        
        plt.tight_layout()
        return self._save_diagram_as_base64(fig)
    
    def generate_api_flow_diagram(self, api_endpoints: List[Dict]) -> str:
        """Generate API flow diagram"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        ax.text(6, 9.5, 'API Architecture Flow', fontsize=20, fontweight='bold', 
                ha='center', color=self.colors['dark'])
        
        # Client
        client = FancyBboxPatch((0.5, 7.5), 2.5, 1, boxstyle="round,pad=0.1",
                               facecolor=self.colors['primary'], edgecolor='white', linewidth=2)
        ax.add_patch(client)
        ax.text(1.75, 8, 'Client\nApplication', fontsize=12, fontweight='bold', 
                ha='center', va='center', color='white')
        
        # API Gateway
        gateway = FancyBboxPatch((4.75, 7.5), 2.5, 1, boxstyle="round,pad=0.1",
                                facecolor=self.colors['secondary'], edgecolor='white', linewidth=2)
        ax.add_patch(gateway)
        ax.text(6, 8, 'API Gateway\n/Load Balancer', fontsize=12, fontweight='bold', 
                ha='center', va='center', color='white')
        
        # Services
        service_y_positions = [6, 4.5, 3]
        service_colors = [self.colors['accent'], self.colors['success'], '#8E44AD']
        
        for i, (y_pos, color) in enumerate(zip(service_y_positions, service_colors)):
            service = FancyBboxPatch((4.75, y_pos), 2.5, 1, boxstyle="round,pad=0.1",
                                    facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(service)
            
            if i < len(api_endpoints):
                endpoint = api_endpoints[i]
                service_name = endpoint.get('path', f'/service{i+1}').split('/')[-1].title()
                method = endpoint.get('method', 'GET')
            else:
                service_name = f'Service {i+1}'
                method = 'GET'
            
            ax.text(6, y_pos + 0.5, f'{service_name}\nService', fontsize=11, fontweight='bold', 
                    ha='center', va='center', color='white')
            ax.text(6, y_pos + 0.1, f'{method}', fontsize=9, 
                    ha='center', va='center', color='white', style='italic')
        
        # Database
        db = FancyBboxPatch((9, 4.5), 2.5, 1, boxstyle="round,pad=0.1",
                           facecolor=self.colors['dark'], edgecolor='white', linewidth=2)
        ax.add_patch(db)
        ax.text(10.25, 5, 'Database\nCluster', fontsize=12, fontweight='bold', 
                ha='center', va='center', color='white')
        
        # Add arrows
        arrow_props = dict(arrowstyle='->', lw=2, color=self.colors['dark'])
        
        # Client to Gateway
        ax.annotate('', xy=(4.75, 8), xytext=(3, 8), arrowprops=arrow_props)
        ax.text(3.9, 8.2, 'HTTPS', fontsize=9, ha='center', color=self.colors['text'])
        
        # Gateway to Services
        for y_pos in service_y_positions:
            ax.annotate('', xy=(4.75, y_pos + 0.5), xytext=(6, 7.5), arrowprops=arrow_props)
        
        # Services to Database
        for y_pos in service_y_positions:
            ax.annotate('', xy=(9, 5), xytext=(7.25, y_pos + 0.5), arrowprops=arrow_props)
        
        plt.tight_layout()
        return self._save_diagram_as_base64(fig)
    
    def generate_component_diagram(self, components: List[str], pages_count: int = 0) -> str:
        """Generate component architecture diagram"""
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        ax.text(5, 9.5, 'Component Architecture', fontsize=20, fontweight='bold', 
                ha='center', color=self.colors['dark'])
        
        # Main App Container
        app_container = FancyBboxPatch((1, 7), 8, 1.5, boxstyle="round,pad=0.1",
                                      facecolor=self.colors['light'], edgecolor=self.colors['primary'], linewidth=3)
        ax.add_patch(app_container)
        ax.text(5, 7.75, 'Application Container', fontsize=16, fontweight='bold', 
                ha='center', color=self.colors['dark'])
        
        # Component grid
        component_positions = [
            (2, 5.5), (5, 5.5), (8, 5.5),  # Top row
            (2, 4), (5, 4), (8, 4),         # Middle row
            (2, 2.5), (5, 2.5), (8, 2.5)   # Bottom row
        ]
        
        component_colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent']] * 3
        
        for i, ((x, y), color) in enumerate(zip(component_positions, component_colors)):
            if i >= len(components) and i >= 6:  # Limit to 6 components max
                break
                
            comp_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='white', linewidth=1)
            ax.add_patch(comp_box)
            
            if i < len(components):
                comp_name = components[i][:12] + '...' if len(components[i]) > 12 else components[i]
            else:
                comp_name = f'Component {i+1}'
            
            ax.text(x, y, comp_name, fontsize=10, fontweight='bold', 
                    ha='center', va='center', color='white')
        
        # Add connection lines
        for i in range(min(len(component_positions), 6)):
            x, y = component_positions[i]
            ax.plot([5, x], [7, y+0.4], '--', color=self.colors['text'], alpha=0.5, linewidth=1)
        
        # Stats box
        stats_box = FancyBboxPatch((1, 0.5), 8, 1, boxstyle="round,pad=0.1",
                                  facecolor=self.colors['light'], edgecolor=self.colors['dark'], linewidth=2)
        ax.add_patch(stats_box)
        
        stats_text = f"Total Components: {len(components)}"
        if pages_count > 0:
            stats_text += f" • Pages: {pages_count}"
        
        ax.text(5, 1, stats_text, fontsize=12, fontweight='bold', 
                ha='center', va='center', color=self.colors['dark'])
        
        plt.tight_layout()
        return self._save_diagram_as_base64(fig)
    
    def _save_diagram_as_base64(self, fig) -> str:
        """Save matplotlib figure as base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"