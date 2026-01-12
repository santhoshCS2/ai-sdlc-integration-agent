import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import os
import time
from typing import Dict, List, Any

class ArchitectureDiagramGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        
    def generate_system_architecture_diagram(self, repo_analysis: Dict, prd_analysis: Dict, endpoints: List[Dict]) -> str:
        """Generate clean professional 5-column system architecture diagram"""
        
        # Create figure with professional dimensions
        fig, ax = plt.subplots(1, 1, figsize=(20, 12))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 12)
        ax.axis('off')
        ax.set_facecolor('white')
        
        # Get real tech stack
        frontend_tech_list = repo_analysis.get('frontend_tech', ['React'])
        backend_tech_list = repo_analysis.get('backend_tech', ['Python'])
        database_tech_list = repo_analysis.get('database_tech', ['PostgreSQL'])
        
        frontend_tech = frontend_tech_list[0] if frontend_tech_list else 'React'
        backend_tech = backend_tech_list[0] if backend_tech_list else 'Python'
        database_tech = database_tech_list[0] if database_tech_list else 'PostgreSQL'
        
        # Extract real data
        entities = self._extract_entities_from_endpoints(endpoints)
        services = self._extract_backend_services_from_endpoints(endpoints)
        api_count = len(endpoints)
        
        # Add title with real data
        product_name = prd_analysis.get('product_name', 'System')
        plt.suptitle(f'{product_name} - System Architecture Overview', 
                    fontsize=20, fontweight='bold', y=0.95)
        
        # Draw 5 columns left to right
        self._draw_column_1_users(ax)
        self._draw_column_2_frontend(ax, frontend_tech, entities)
        self._draw_column_3_api_gateway(ax, backend_tech, api_count)
        self._draw_column_4_backend_services(ax, services)
        self._draw_column_5_databases(ax, database_tech, entities)
        
        # Draw flow arrows left to right
        self._draw_left_to_right_flow(ax)
        
        # Save diagram
        filename = f"system_architecture_{product_name.replace(' ', '_')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath
    
    def _extract_entities_from_endpoints(self, endpoints: List[Dict]) -> List[str]:
        """Extract unique entities from API endpoints"""
        entities = set()
        for ep in endpoints:
            if isinstance(ep, dict):
                path = ep.get('path', '')
                parts = [p for p in path.split('/') if p and p != 'api']
                for part in parts:
                    if part not in ['auth', 'login', 'register', 'health']:
                        entities.add(part.lower())
        return list(entities)[:5]  # Limit to 5 main entities
    
    def _extract_backend_services_from_endpoints(self, endpoints: List[Dict]) -> List[str]:
        """Extract backend services from API endpoints"""
        services = set()
        
        for ep in endpoints:
            if isinstance(ep, dict):
                path = ep.get('path', '')
                parts = [p for p in path.split('/') if p and p != 'api']
                if parts:
                    service_name = parts[0]
                    if service_name not in ['health', 'status']:
                        services.add(f"{service_name.title()} Service")
        
        service_list = list(services)
        if not service_list:
            service_list = ['User Service', 'Data Service', 'Auth Service']
        
        return service_list[:3]  # Limit to 3 main services
    
    def _draw_column_1_users(self, ax):
        """Draw Column 1: Users/Clients (light green)"""
        # Column header
        ax.text(2, 11, 'Users/Clients', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # User components
        users = [
            ('Web Users', 9.5),
            ('Mobile Users', 8),
            ('All Public Users', 6.5)
        ]
        
        for user_type, y_pos in users:
            user_box = FancyBboxPatch((0.5, y_pos-0.4), 3, 0.8, boxstyle="round,pad=0.1",
                                     facecolor='lightgreen', edgecolor='darkgreen', linewidth=1.5)
            ax.add_patch(user_box)
            ax.text(2, y_pos, user_type, ha='center', va='center', fontsize=10, fontweight='bold')
    
    def _draw_column_2_frontend(self, ax, tech: str, entities: List[str]):
        """Draw Column 2: Frontend UI (light teal)"""
        # Column header
        ax.text(6, 11, 'Frontend UI', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Main frontend application
        main_box = FancyBboxPatch((4.5, 8.5), 3, 1.2, boxstyle="round,pad=0.1",
                                 facecolor='lightcyan', edgecolor='darkcyan', linewidth=2)
        ax.add_patch(main_box)
        ax.text(6, 9.1, f'{tech} Application', ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Frontend components based on entities
        components = []
        if entities:
            for entity in entities[:3]:
                components.append(f'{entity.title()} Management')
        else:
            components = ['Dashboard', 'User Interface', 'Settings']
        
        for i, component in enumerate(components):
            comp_box = FancyBboxPatch((4.5, 7-i*1.2), 3, 0.8, boxstyle="round,pad=0.05",
                                     facecolor='lightcyan', edgecolor='teal', linewidth=1)
            ax.add_patch(comp_box)
            ax.text(6, 7.4-i*1.2, component, ha='center', va='center', fontsize=9)
    
    def _draw_column_3_api_gateway(self, ax, backend_tech: str, api_count: int):
        """Draw Column 3: API Gateway (light yellow/orange)"""
        # Column header
        ax.text(10, 11, 'API Gateway', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Main API Gateway (prominent hexagon-like box)
        gateway_box = FancyBboxPatch((8.5, 7), 3, 2.5, boxstyle="round,pad=0.15",
                                    facecolor='lightyellow', edgecolor='orange', linewidth=3)
        ax.add_patch(gateway_box)
        ax.text(10, 8.7, f'{backend_tech} Backend', ha='center', va='center', fontsize=12, fontweight='bold')
        ax.text(10, 8.3, 'Central API Entry Point', ha='center', va='center', fontsize=10)
        ax.text(10, 7.9, f'{api_count} RESTful APIs', ha='center', va='center', fontsize=10)
        ax.text(10, 7.5, 'Routing & Authentication', ha='center', va='center', fontsize=9)
        ax.text(10, 7.1, 'Rate Limiting', ha='center', va='center', fontsize=9)
    
    def _draw_column_4_backend_services(self, ax, services: List[str]):
        """Draw Column 4: Backend Services (light orange)"""
        # Column header
        ax.text(14, 11, 'Backend Services', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Backend services
        for i, service in enumerate(services[:3]):
            service_box = FancyBboxPatch((12.5, 9-i*2), 3, 1.2, boxstyle="round,pad=0.1",
                                        facecolor='lightsalmon', edgecolor='darkorange', linewidth=2)
            ax.add_patch(service_box)
            ax.text(14, 9.6-i*2, service, ha='center', va='center', fontsize=11, fontweight='bold')
            ax.text(14, 9.2-i*2, 'Business Logic', ha='center', va='center', fontsize=9)
    
    def _draw_column_5_databases(self, ax, database_tech: str, entities: List[str]):
        """Draw Column 5: Databases (light purple)"""
        # Column header
        ax.text(18, 11, 'Databases', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Main database
        db_box = FancyBboxPatch((16.5, 7.5), 3, 2, boxstyle="round,pad=0.1",
                               facecolor='plum', edgecolor='purple', linewidth=2)
        ax.add_patch(db_box)
        ax.text(18, 8.8, f'{database_tech}', ha='center', va='center', fontsize=12, fontweight='bold')
        ax.text(18, 8.4, '(Primary Database)', ha='center', va='center', fontsize=10)
        
        # Database tables based on entities
        tables = []
        if entities:
            for entity in entities[:4]:
                tables.append(f'{entity}_table')
        else:
            tables = ['users', 'data', 'sessions', 'logs']
        
        # Tables box
        tables_box = FancyBboxPatch((16.5, 5), 3, 2, boxstyle="round,pad=0.1",
                                   facecolor='lavender', edgecolor='purple', linewidth=1)
        ax.add_patch(tables_box)
        ax.text(18, 6.5, 'Key Tables:', ha='center', va='center', fontsize=10, fontweight='bold')
        
        for i, table in enumerate(tables[:4]):
            ax.text(18, 6.1-i*0.3, f'• {table}', ha='center', va='center', fontsize=9)
        
        # ORM note
        ax.text(18, 4.5, 'SQLAlchemy ORM', ha='center', va='center', fontsize=9, style='italic')
    
    def _draw_left_to_right_flow(self, ax):
        """Draw clean left-to-right flow arrows"""
        # Users to Frontend
        con1 = ConnectionPatch((3.5, 8), (4.5, 8), "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="blue", linewidth=2)
        ax.add_patch(con1)
        
        # Frontend to API Gateway
        con2 = ConnectionPatch((7.5, 8.2), (8.5, 8.2), "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="green", linewidth=2)
        ax.add_patch(con2)
        ax.text(8, 8.5, 'HTTPS', ha='center', va='center', fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
        
        # API Gateway to Backend Services
        con3 = ConnectionPatch((11.5, 8.2), (12.5, 8.2), "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="orange", linewidth=2)
        ax.add_patch(con3)
        ax.text(12, 8.5, 'REST API', ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
        
        # Backend Services to Database
        con4 = ConnectionPatch((15.5, 8.2), (16.5, 8.2), "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="purple", linewidth=2)
        ax.add_patch(con4)
        ax.text(16, 8.5, 'SQL/ORM', ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

    def generate_sequence_diagram(self, project_name: str, entity_name: str, endpoints: List[Dict]) -> str:
        """Generate a truly dynamic sequence diagram based on actual detected endpoints"""
        
        # Setup figure
        fig, ax = plt.subplots(1, 1, figsize=(14, 18))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 24)
        ax.axis('off')
        ax.set_facecolor('white')
        
        # Title
        entity_display = entity_name if entity_name else "Resource"
        
        # Detect what operations are actually available
        operations = self._detect_available_operations(endpoints, entity_display)
        operation_text = " + ".join(operations) if operations else "API Interactions"
        
        plt.suptitle(f'System Interaction Flow: {project_name}\n({entity_display} Operations: {operation_text})', 
                    fontsize=16, fontweight='bold', y=0.95, color='#2c3e50')

        # Participants (dynamically determine based on detected tech)
        actors = [
            {'name': 'User\n(Browser)', 'x': 2},
            {'name': 'Frontend\n(React/Next)', 'x': 7},
            {'name': 'Backend\n(API)', 'x': 12},
            {'name': 'Database\n(DB)', 'x': 17}
        ]

        # Draw Lifelines
        for actor in actors:
            # Header
            rect = FancyBboxPatch((actor['x']-1.5, 21), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#ecf0f1', edgecolor='#2c3e50', linewidth=1.5)
            ax.add_patch(rect)
            ax.text(actor['x'], 21.75, actor['name'], ha='center', va='center', fontsize=11, fontweight='bold')
            
            # Vertical Line
            ax.plot([actor['x'], actor['x']], [1, 21], color='#7f8c8d', linestyle='--', linewidth=1.5)

        # Generate dynamic sequence steps based on actual endpoints
        steps = self._generate_dynamic_steps(endpoints, entity_display)
        
        # Draw steps
        current_y = 20.0
        step_gap = 1.4
        step_number = 1

        for step in steps:
            # Add extra gap for logical separation
            if step.get('gap'):
                current_y -= 1.0

            src_x = actors[step['src']]['x']
            dst_x = actors[step['dst']]['x']
            
            # Arrow properties based on type
            if step['type'] == 'req':
                arrow_style = '-|>'  # Solid head for requests
                line_style = '-'
                color = '#2980b9'  # Blue
            elif step['type'] == 'res':
                arrow_style = '->'  # Open head for responses
                line_style = '--'
                color = '#27ae60'  # Green
            else:  # 'action' type
                arrow_style = '-|>'
                line_style = ':'
                color = '#e67e22'  # Orange for user actions

            # Draw Arrow
            ax.annotate('', xy=(dst_x, current_y), xytext=(src_x, current_y),
                        arrowprops=dict(arrowstyle=arrow_style, linestyle=line_style, color=color, linewidth=1.5))
            
            # Label Text (with step number)
            mid_x = (src_x + dst_x) / 2
            label_with_number = f"{step_number}. {step['label']}"
            ax.text(mid_x, current_y + 0.2, label_with_number, ha='center', va='bottom', 
                   fontsize=10, color='#34495e', backgroundcolor='white')
            
            current_y -= step_gap
            step_number += 1

        # Save diagram
        filename = f"sequence_diagram_{entity_display.lower()}_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath
    
    def _detect_available_operations(self, endpoints: List[Dict], entity: str) -> List[str]:
        """Detect what operations are actually available for this entity"""
        operations = []
        entity_lower = entity.lower()
        
        # Find endpoints related to this entity
        related_endpoints = []
        for ep in endpoints:
            if isinstance(ep, dict):
                path = ep.get('path', '').lower()
                if entity_lower in path or entity_lower.rstrip('s') in path:
                    related_endpoints.append(ep)
        
        # Detect operations
        methods = [ep.get('method', '') for ep in related_endpoints]
        
        if 'GET' in methods:
            operations.append('List')
        if 'POST' in methods:
            operations.append('Create')
        if 'PUT' in methods or 'PATCH' in methods:
            operations.append('Update')
        if 'DELETE' in methods:
            operations.append('Delete')
        
        return operations if operations else ['CRUD']
    
    def _generate_dynamic_steps(self, endpoints: List[Dict], entity: str) -> List[Dict]:
        """Generate sequence steps dynamically based on actual detected endpoints"""
        steps = []
        entity_lower = entity.lower()
        
        # Find related endpoints
        related_endpoints = []
        for ep in endpoints:
            if isinstance(ep, dict):
                path = ep.get('path', '').lower()
                if entity_lower in path or entity_lower.rstrip('s') in path:
                    related_endpoints.append(ep)
        
        # If no specific endpoints found, generate generic flow
        if not related_endpoints:
            return self._generate_generic_flow(entity)
        
        # Group by method
        get_endpoints = [ep for ep in related_endpoints if ep.get('method') == 'GET']
        post_endpoints = [ep for ep in related_endpoints if ep.get('method') == 'POST']
        put_endpoints = [ep for ep in related_endpoints if ep.get('method') in ['PUT', 'PATCH']]
        delete_endpoints = [ep for ep in related_endpoints if ep.get('method') == 'DELETE']
        
        # Generate flow based on what's available
        
        # LIST/GET Flow
        if get_endpoints:
            get_ep = get_endpoints[0]
            steps.extend([
                {'src': 0, 'dst': 1, 'label': f'Navigate to {entity} page', 'type': 'action'},
                {'src': 1, 'dst': 2, 'label': f'{get_ep.get("method")} {get_ep.get("path")}', 'type': 'req'},
                {'src': 2, 'dst': 3, 'label': f'Query {entity} table', 'type': 'req'},
                {'src': 3, 'dst': 2, 'label': 'Return records', 'type': 'res'},
                {'src': 2, 'dst': 1, 'label': '200 OK + JSON data', 'type': 'res'},
                {'src': 1, 'dst': 0, 'label': f'Display {entity} list', 'type': 'res'},
            ])
        
        # CREATE/POST Flow
        if post_endpoints:
            post_ep = post_endpoints[0]
            steps.append({'gap': True})  # Visual separator
            steps.extend([
                {'src': 0, 'dst': 1, 'label': 'Click "Create New"', 'type': 'action'},
                {'src': 1, 'dst': 2, 'label': f'{post_ep.get("method")} {post_ep.get("path")}\n(with form data)', 'type': 'req'},
                {'src': 2, 'dst': 3, 'label': f'INSERT INTO {entity}', 'type': 'req'},
                {'src': 3, 'dst': 2, 'label': 'Return new ID', 'type': 'res'},
                {'src': 2, 'dst': 1, 'label': '201 Created', 'type': 'res'},
                {'src': 1, 'dst': 0, 'label': 'Show success & refresh', 'type': 'res'},
            ])
        
        # UPDATE Flow (if exists)
        if put_endpoints:
            put_ep = put_endpoints[0]
            steps.append({'gap': True})
            steps.extend([
                {'src': 0, 'dst': 1, 'label': 'Edit existing item', 'type': 'action'},
                {'src': 1, 'dst': 2, 'label': f'{put_ep.get("method")} {put_ep.get("path")}\n(with updates)', 'type': 'req'},
                {'src': 2, 'dst': 3, 'label': f'UPDATE {entity} SET...', 'type': 'req'},
                {'src': 3, 'dst': 2, 'label': 'Confirm update', 'type': 'res'},
                {'src': 2, 'dst': 1, 'label': '200 OK', 'type': 'res'},
                {'src': 1, 'dst': 0, 'label': 'Update UI', 'type': 'res'},
            ])
        
        # DELETE Flow (if exists)
        if delete_endpoints:
            delete_ep = delete_endpoints[0]
            steps.append({'gap': True})
            steps.extend([
                {'src': 0, 'dst': 1, 'label': 'Click "Delete"', 'type': 'action'},
                {'src': 1, 'dst': 2, 'label': f'{delete_ep.get("method")} {delete_ep.get("path")}', 'type': 'req'},
                {'src': 2, 'dst': 3, 'label': f'DELETE FROM {entity}', 'type': 'req'},
                {'src': 3, 'dst': 2, 'label': 'Confirm deletion', 'type': 'res'},
                {'src': 2, 'dst': 1, 'label': '204 No Content', 'type': 'res'},
                {'src': 1, 'dst': 0, 'label': 'Remove from UI', 'type': 'res'},
            ])
        
        return steps
    
    def _generate_generic_flow(self, entity: str) -> List[Dict]:
        """Generate a generic flow when no specific endpoints are detected"""
        return [
            {'src': 0, 'dst': 1, 'label': f'Access {entity} interface', 'type': 'action'},
            {'src': 1, 'dst': 2, 'label': f'Request {entity} data', 'type': 'req'},
            {'src': 2, 'dst': 3, 'label': 'Fetch from database', 'type': 'req'},
            {'src': 3, 'dst': 2, 'label': 'Return data', 'type': 'res'},
            {'src': 2, 'dst': 1, 'label': 'Send response', 'type': 'res'},
            {'src': 1, 'dst': 0, 'label': f'Display {entity}', 'type': 'res'},
        ]


    def generate_context_flow_diagram(self, frontend_tech: list, backend_tech: list, database_tech: list) -> str:
        """Generate visual context flow diagram (Client -> Frontend -> Backend -> Database)"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 14)
        ax.axis('off')
        ax.set_facecolor('white')
        
        # Title
        plt.suptitle('Architecture Context Diagram\n(System Data Flow)', 
                    fontsize=16, fontweight='bold', y=0.94, color='#2c3e50')
        
        # Define layers with positions
        layers = [
            {'name': 'CLIENT', 'subtitle': 'User Browser/Mobile', 'y': 11, 'color': '#e74c3c', 'tech': ''},
            {'name': 'FRONTEND', 'subtitle': 'Presentation Logic', 'y': 8, 'color': '#3498db', 'tech': ', '.join(frontend_tech) if frontend_tech else 'React'},
            {'name': 'BACKEND', 'subtitle': 'Business Logic', 'y': 5, 'color': '#2ecc71', 'tech': ', '.join(backend_tech) if backend_tech else 'FastAPI'},
            {'name': 'DATABASE', 'subtitle': 'Persistent Data', 'y': 2, 'color': '#9b59b6', 'tech': ', '.join(database_tech) if database_tech else 'PostgreSQL'}
        ]
        
        # Draw boxes and arrows
        for i, layer in enumerate(layers):
            # Box
            box = FancyBboxPatch((5, layer['y']-0.6), 10, 1.8, boxstyle="round,pad=0.15",
                                facecolor=layer['color'], edgecolor='#2c3e50', linewidth=2, alpha=0.85)
            ax.add_patch(box)
            
            # Text
            ax.text(10, layer['y']+0.5, f"■ {layer['name']} ■", ha='center', va='center',
                   fontsize=14, fontweight='bold', color='white')
            ax.text(10, layer['y'], layer['subtitle'], ha='center', va='center',
                   fontsize=10, color='white', style='italic')
            if layer['tech']:
                ax.text(10, layer['y']-0.4, f"({layer['tech']})", ha='center', va='center',
                       fontsize=9, color='white')
            
            # Arrow to next layer
            if i < len(layers) - 1:
                next_y = layers[i+1]['y']
                arrow_labels = [
                    'HTTP Request / API Call',
                    'Data Fetch / AJAX',
                    'SQL / NoSQL Query'
                ]
                
                # Draw arrow
                ax.annotate('', xy=(10, next_y+0.6), xytext=(10, layer['y']-0.8),
                           arrowprops=dict(arrowstyle='-|>', color='#34495e', linewidth=2.5, lw=2))
                
                # Arrow label
                mid_y = (layer['y'] + next_y) / 2
                ax.text(10, mid_y, f'▼ ({arrow_labels[i]})', ha='center', va='center',
                       fontsize=9, color='#34495e', backgroundcolor='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.9))
        
        # Save
        filename = f"context_flow_diagram_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath

    def generate_frontend_architecture_diagram(self, frontend_tech: list, components_count: int, component_names: list) -> str:
        """Generate visual frontend architecture diagram"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 16)
        ax.axis('off')
        ax.set_facecolor('#f8f9fa')
        
        # Title
        framework = frontend_tech[0] if frontend_tech else 'React'
        plt.suptitle(f'Frontend Architecture\n({framework} Application)', 
                    fontsize=16, fontweight='bold', y=0.94, color='#2c3e50')
        
        # Main container
        container = FancyBboxPatch((1, 1), 18, 13, boxstyle="round,pad=0.2",
                                  facecolor='white', edgecolor='#3498db', linewidth=2.5)
        ax.add_patch(container)
        ax.text(10, 13.5, f'{framework} Application', ha='center', va='center',
               fontsize=13, fontweight='bold', color='#3498db')
        
        # Components section
        comp_box = FancyBboxPatch((2, 9), 16, 3.5, boxstyle="round,pad=0.15",
                                 facecolor='#e3f2fd', edgecolor='#2196f3', linewidth=1.5)
        ax.add_patch(comp_box)
        ax.text(10, 12, f'Components ({components_count} total)', ha='center', va='center',
               fontsize=11, fontweight='bold', color='#1976d2')
        
        # Show component names
        if component_names:
            comp_text = ', '.join(component_names[:6])  # Show first 6
            if len(component_names) > 6:
                comp_text += f', +{len(component_names)-6} more'
            ax.text(10, 10.5, comp_text, ha='center', va='center',
                   fontsize=9, color='#424242', style='italic')
        else:
            ax.text(10, 10.5, 'UI Components, Pages, Layouts', ha='center', va='center',
                   fontsize=9, color='#424242', style='italic')
        
        # Routing section
        routing_box = FancyBboxPatch((2, 6.5), 7, 2, boxstyle="round,pad=0.15",
                                    facecolor='#fff3e0', edgecolor='#ff9800', linewidth=1.5)
        ax.add_patch(routing_box)
        ax.text(5.5, 7.8, 'Routing', ha='center', va='center',
               fontsize=10, fontweight='bold', color='#e65100')
        ax.text(5.5, 7.2, '• Page Navigation\n• Route Guards', ha='center', va='center',
               fontsize=8, color='#424242')
        
        # State Management section
        state_box = FancyBboxPatch((11, 6.5), 7, 2, boxstyle="round,pad=0.15",
                                  facecolor='#f3e5f5', edgecolor='#9c27b0', linewidth=1.5)
        ax.add_patch(state_box)
        ax.text(14.5, 7.8, 'State Management', ha='center', va='center',
               fontsize=10, fontweight='bold', color='#6a1b9a')
        ax.text(14.5, 7.2, '• Global State\n• Local State', ha='center', va='center',
               fontsize=8, color='#424242')
        
        # API Communication section
        api_box = FancyBboxPatch((2, 3.5), 16, 2.5, boxstyle="round,pad=0.15",
                                facecolor='#e8f5e9', edgecolor='#4caf50', linewidth=1.5)
        ax.add_patch(api_box)
        ax.text(10, 5.3, 'API Communication Layer', ha='center', va='center',
               fontsize=10, fontweight='bold', color='#2e7d32')
        ax.text(10, 4.5, '• HTTP Requests  • Data Fetching  • Error Handling', ha='center', va='center',
               fontsize=8, color='#424242')
        
        # Arrow to backend
        ax.annotate('', xy=(10, 1.5), xytext=(10, 3.3),
                   arrowprops=dict(arrowstyle='-|>', color='#2ecc71', linewidth=2.5))
        ax.text(10, 2.3, 'API Calls', ha='center', va='center',
               fontsize=9, color='#27ae60', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#2ecc71'))
        
        # Save
        filename = f"frontend_architecture_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#f8f9fa', edgecolor='none')
        plt.close()
        
        return filepath

    def generate_backend_architecture_diagram(self, backend_tech: list, api_count: int, database_tech: list) -> str:
        """Generate visual backend architecture diagram"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 16)
        ax.axis('off')
        ax.set_facecolor('#fafafa')
        
        # Title
        framework = backend_tech[0] if backend_tech else 'FastAPI'
        plt.suptitle(f'Backend Architecture\n({framework} Service)', 
                    fontsize=16, fontweight='bold', y=0.94, color='#2c3e50')
        
        # Main container
        container = FancyBboxPatch((1, 1), 18, 13, boxstyle="round,pad=0.2",
                                  facecolor='white', edgecolor='#2ecc71', linewidth=2.5)
        ax.add_patch(container)
        ax.text(10, 13.5, f'{framework} Backend Service', ha='center', va='center',
               fontsize=13, fontweight='bold', color='#2ecc71')
        
        # API Layer
        api_box = FancyBboxPatch((2, 10), 16, 2.5, boxstyle="round,pad=0.15",
                                facecolor='#e3f2fd', edgecolor='#2196f3', linewidth=1.5)
        ax.add_patch(api_box)
        ax.text(10, 11.8, f'API Endpoints ({api_count} total)', ha='center', va='center',
               fontsize=11, fontweight='bold', color='#1565c0')
        ax.text(10, 11, 'RESTful Services • CRUD Operations • Request Validation', ha='center', va='center',
               fontsize=9, color='#424242')
        
        # Business Logic Layer
        logic_box = FancyBboxPatch((2, 7), 16, 2.5, boxstyle="round,pad=0.15",
                                  facecolor='#fff3e0', edgecolor='#ff9800', linewidth=1.5)
        ax.add_patch(logic_box)
        ax.text(10, 8.8, 'Business Logic Layer', ha='center', va='center',
               fontsize=11, fontweight='bold', color='#e65100')
        ax.text(10, 8, 'Service Classes • Data Processing • Business Rules', ha='center', va='center',
               fontsize=9, color='#424242')
        
        # Data Access Layer
        data_box = FancyBboxPatch((2, 4), 16, 2.5, boxstyle="round,pad=0.15",
                                 facecolor='#f3e5f5', edgecolor='#9c27b0', linewidth=1.5)
        ax.add_patch(data_box)
        ax.text(10, 5.8, 'Data Access Layer', ha='center', va='center',
               fontsize=11, fontweight='bold', color='#6a1b9a')
        db_name = database_tech[0] if database_tech else 'PostgreSQL'
        ax.text(10, 5, f'ORM/ODM • Query Builder • {db_name} Integration', ha='center', va='center',
               fontsize=9, color='#424242')
        
        # Arrows between layers
        # API -> Business Logic
        ax.annotate('', xy=(10, 9.3), xytext=(10, 10),
                   arrowprops=dict(arrowstyle='-|>', color='#34495e', linewidth=2))
        
        # Business Logic -> Data Access
        ax.annotate('', xy=(10, 6.3), xytext=(10, 7),
                   arrowprops=dict(arrowstyle='-|>', color='#34495e', linewidth=2))
        
        # Data Access -> Database
        ax.annotate('', xy=(10, 2), xytext=(10, 3.8),
                   arrowprops=dict(arrowstyle='-|>', color='#9b59b6', linewidth=2.5))
        ax.text(10, 2.8, 'SQL Queries', ha='center', va='center',
               fontsize=9, color='#8e44ad', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#9b59b6'))
        
        # Save
        filename = f"backend_architecture_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#fafafa', edgecolor='none')
        plt.close()
        
        return filepath