import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import os
import time
import re
from typing import Dict, List, Any, Tuple

class LayeredDataFlowGenerator:
    """Generate complex layered data flow diagrams dynamically from repository analysis"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.colors = {
            'acquisition': '#e3f2fd',
            'knowledge': '#fff3e0',
            'application': '#e8f5e9',
            'presentation': '#f3e5f5',
            'storage': '#fce4ec',
            'security': '#fff9c4',
            'cicd': '#e0f2f1',
            'external': '#ffebee'
        }
    
    def generate_layered_dataflow_diagram(self, repo_analysis: Dict, prd_analysis: Dict, endpoints: List[Dict]) -> str:
        """Generate comprehensive layered data flow diagram"""
        
        # Detect all layers and components
        layers = self._detect_all_layers(repo_analysis, prd_analysis, endpoints)
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(20, 14))
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 18)
        ax.axis('off')
        ax.set_facecolor('#fafafa')
        
        # Title
        product_name = prd_analysis.get('product_name', 'System')
        plt.suptitle(f'{product_name} - Layered Architecture Data Flow', 
                    fontsize=18, fontweight='bold', y=0.96, color='#1a237e')
        
        # Draw layers from top to bottom
        y_positions = {
            'presentation': 15,
            'application': 11.5,
            'knowledge': 8,
            'acquisition': 4.5,
            'storage': 1
        }
        
        # Draw each layer
        for layer_name, y_pos in y_positions.items():
            if layer_name in layers and layers[layer_name]['components']:
                self._draw_layer(ax, layer_name, layers[layer_name], y_pos)
        
        # Draw security layer (vertical on right side)
        if 'security' in layers and layers['security']['components']:
            self._draw_security_layer(ax, layers['security'])
        
        # Draw CI/CD tools at bottom
        if 'cicd' in layers and layers['cicd']['components']:
            self._draw_cicd_layer(ax, layers['cicd'])
        
        # Draw external systems (left side)
        if 'external' in layers and layers['external']['components']:
            self._draw_external_systems(ax, layers['external'])
        
        # Draw data flow arrows
        self._draw_data_flows(ax, layers)
        
        # Save
        filename = f"layered_dataflow_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#fafafa', edgecolor='none')
        plt.close()
        
        return filepath
    
    def _detect_all_layers(self, repo_analysis: Dict, prd_analysis: Dict, endpoints: List[Dict]) -> Dict:
        """Detect all architecture layers and their components"""
        
        layers = {
            'presentation': {'components': [], 'description': 'User Interface & Visualization'},
            'application': {'components': [], 'description': 'Business Logic & APIs'},
            'knowledge': {'components': [], 'description': 'Processing & Analytics'},
            'acquisition': {'components': [], 'description': 'Data Collection & Input'},
            'storage': {'components': [], 'description': 'Persistent Data'},
            'security': {'components': [], 'description': 'Authentication & Authorization'},
            'cicd': {'components': [], 'description': 'Build & Deployment'},
            'external': {'components': [], 'description': 'External Systems'}
        }
        
        # Presentation Layer
        frontend_tech = repo_analysis.get('frontend_tech', [])
        if frontend_tech:
            layers['presentation']['components'].extend([
                {'name': tech, 'type': 'framework'} for tech in frontend_tech[:2]
            ])
        
        components = repo_analysis.get('components_total', 0)
        if components > 0:
            layers['presentation']['components'].append({
                'name': f'UI Components ({components})',
                'type': 'components'
            })
        
        # Check for dashboards/analytics in PRD
        prd_content = prd_analysis.get('content', '').lower()
        if any(word in prd_content for word in ['dashboard', 'visualization', 'chart', 'graph']):
            layers['presentation']['components'].append({
                'name': 'Dashboards',
                'type': 'feature'
            })
        
        # Application Layer
        backend_tech = repo_analysis.get('backend_tech', [])
        if backend_tech:
            layers['application']['components'].extend([
                {'name': tech, 'type': 'framework'} for tech in backend_tech[:2]
            ])
        
        if endpoints:
            layers['application']['components'].append({
                'name': f'REST API ({len(endpoints)} endpoints)',
                'type': 'api'
            })
        
        # Knowledge Layer (ML, Analytics, Processing)
        folder_structure = repo_analysis.get('folder_structure', {})
        
        # Check for ML/AI components
        ml_indicators = []
        for folder, info in folder_structure.items():
            if isinstance(info, dict) and 'files' in info:
                for file in info['files']:
                    if file.endswith(('.pkl', '.h5', '.pt', '.pth', '.model')):
                        ml_indicators.append('ML Models')
                        break
                    if file in ['train.py', 'model.py', 'predict.py']:
                        ml_indicators.append('ML Pipeline')
                        break
        
        if ml_indicators:
            layers['knowledge']['components'].extend([
                {'name': indicator, 'type': 'ml'} for indicator in set(ml_indicators)
            ])
        
        # Check for analytics/processing in PRD
        if any(word in prd_content for word in ['analytics', 'machine learning', 'ai', 'prediction', 'analysis']):
            if not ml_indicators:
                layers['knowledge']['components'].append({
                    'name': 'Analytics Engine',
                    'type': 'processing'
                })
        
        # Acquisition Layer
        # Check for data collection, forms, IoT
        if any(word in prd_content for word in ['sensor', 'iot', 'device', 'wearable']):
            layers['acquisition']['components'].append({
                'name': 'IoT Sensors',
                'type': 'input'
            })
        
        if any(word in prd_content for word in ['form', 'input', 'user data', 'upload']):
            layers['acquisition']['components'].append({
                'name': 'User Input Forms',
                'type': 'input'
            })
        
        # Check for batch processing
        for folder, info in folder_structure.items():
            if isinstance(info, dict) and 'files' in info:
                if any(f in info['files'] for f in ['batch.py', 'cron.py', 'scheduler.py']):
                    layers['acquisition']['components'].append({
                        'name': 'Batch Processing',
                        'type': 'batch'
                    })
                    break
        
        # Storage Layer
        database_tech = repo_analysis.get('database_tech', [])
        if database_tech:
            layers['storage']['components'].extend([
                {'name': tech, 'type': 'database'} for tech in database_tech[:2]
            ])
        
        # Check for caching
        if any(word in prd_content for word in ['redis', 'cache', 'memcached']):
            layers['storage']['components'].append({
                'name': 'Cache (Redis)',
                'type': 'cache'
            })
        
        # Check for file storage
        if any(word in prd_content for word in ['s3', 'storage', 'file upload', 'media']):
            layers['storage']['components'].append({
                'name': 'File Storage',
                'type': 'storage'
            })
        
        # Security Layer
        auth_endpoints = [ep for ep in endpoints if isinstance(ep, dict) and 
                         any(word in ep.get('path', '').lower() for word in ['auth', 'login', 'token', 'oauth'])]
        
        if auth_endpoints:
            layers['security']['components'].append({
                'name': 'Authentication',
                'type': 'auth'
            })
        
        if any(word in prd_content for word in ['jwt', 'oauth', 'saml', 'sso']):
            layers['security']['components'].append({
                'name': 'OAuth/JWT',
                'type': 'auth'
            })
        
        if any(word in prd_content for word in ['encryption', 'ssl', 'tls', 'https']):
            layers['security']['components'].append({
                'name': 'Encryption',
                'type': 'security'
            })
        
        # CI/CD Layer
        cicd_files = []
        for folder, info in folder_structure.items():
            if isinstance(info, dict) and 'files' in info:
                if 'Dockerfile' in info['files']:
                    cicd_files.append('Docker')
                if 'docker-compose.yml' in info['files']:
                    cicd_files.append('Docker Compose')
                if any('.yml' in f or '.yaml' in f for f in info['files'] if '.github' in folder):
                    cicd_files.append('GitHub Actions')
                if 'Jenkinsfile' in info['files']:
                    cicd_files.append('Jenkins')
        
        if cicd_files:
            layers['cicd']['components'].extend([
                {'name': tool, 'type': 'cicd'} for tool in set(cicd_files)
            ])
        
        # External Systems
        if any(word in prd_content for word in ['api integration', 'third party', 'external api', 'weather', 'payment']):
            # Extract specific external systems
            external_systems = []
            if 'payment' in prd_content or 'stripe' in prd_content:
                external_systems.append('Payment Gateway')
            if 'weather' in prd_content:
                external_systems.append('Weather API')
            if 'map' in prd_content or 'location' in prd_content:
                external_systems.append('Maps API')
            if 'email' in prd_content or 'notification' in prd_content:
                external_systems.append('Email Service')
            
            if external_systems:
                layers['external']['components'].extend([
                    {'name': sys, 'type': 'external'} for sys in external_systems
                ])
            else:
                layers['external']['components'].append({
                    'name': 'External APIs',
                    'type': 'external'
                })
        
        return layers
    
    def _draw_layer(self, ax, layer_name: str, layer_data: Dict, y_pos: float):
        """Draw a horizontal layer with its components"""
        
        components = layer_data['components']
        if not components:
            return
        
        # Layer background
        layer_box = Rectangle((1, y_pos - 0.3), 18, 2.8, 
                              facecolor=self.colors.get(layer_name, '#f0f0f0'),
                              edgecolor='#424242', linewidth=1.5, alpha=0.3)
        ax.add_patch(layer_box)
        
        # Layer title
        ax.text(1.5, y_pos + 2.2, f"{layer_name.upper()} LAYER", 
               fontsize=11, fontweight='bold', color='#1a237e')
        ax.text(1.5, y_pos + 1.8, layer_data['description'], 
               fontsize=8, color='#424242', style='italic')
        
        # Draw components
        num_components = len(components)
        component_width = min(3.5, 16 / max(num_components, 1))
        x_start = 2
        
        for i, component in enumerate(components[:5]):  # Max 5 components per layer
            x_pos = x_start + (i * (component_width + 0.5))
            
            # Component box
            comp_box = FancyBboxPatch((x_pos, y_pos), component_width, 1.5,
                                     boxstyle="round,pad=0.1",
                                     facecolor='white',
                                     edgecolor='#1976d2',
                                     linewidth=1.5)
            ax.add_patch(comp_box)
            
            # Component name
            comp_name = component['name']
            if len(comp_name) > 20:
                comp_name = comp_name[:17] + '...'
            
            ax.text(x_pos + component_width/2, y_pos + 0.75, comp_name,
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   color='#1565c0')
        
        # Show "+" if more components
        if num_components > 5:
            ax.text(x_start + 5 * (component_width + 0.5), y_pos + 0.75,
                   f"+{num_components - 5} more",
                   ha='left', va='center', fontsize=8, color='#757575', style='italic')
    
    def _draw_security_layer(self, ax, security_data: Dict):
        """Draw security layer as vertical bar on right side"""
        
        # Security bar
        sec_box = Rectangle((19.5, 2), 3.5, 14,
                           facecolor=self.colors['security'],
                           edgecolor='#f57c00', linewidth=2, alpha=0.4)
        ax.add_patch(sec_box)
        
        # Title
        ax.text(21.25, 15.5, "SECURITY", ha='center', fontsize=11,
               fontweight='bold', color='#e65100', rotation=0)
        
        # Components
        y_start = 13
        for i, comp in enumerate(security_data['components'][:4]):
            y_pos = y_start - (i * 2.5)
            
            comp_box = FancyBboxPatch((19.8, y_pos), 3, 1.5,
                                     boxstyle="round,pad=0.1",
                                     facecolor='white',
                                     edgecolor='#f57c00',
                                     linewidth=1.5)
            ax.add_patch(comp_box)
            
            ax.text(21.3, y_pos + 0.75, comp['name'],
                   ha='center', va='center', fontsize=8,
                   fontweight='bold', color='#e65100')
    
    def _draw_cicd_layer(self, ax, cicd_data: Dict):
        """Draw CI/CD tools at bottom"""
        
        # CI/CD bar
        cicd_box = Rectangle((1, 0.2), 18, 0.6,
                            facecolor=self.colors['cicd'],
                            edgecolor='#00796b', linewidth=1.5, alpha=0.5)
        ax.add_patch(cicd_box)
        
        # Title and tools
        tools_text = " | ".join([comp['name'] for comp in cicd_data['components'][:6]])
        ax.text(10, 0.5, f"CI/CD: {tools_text}",
               ha='center', va='center', fontsize=9,
               fontweight='bold', color='#004d40')
    
    def _draw_external_systems(self, ax, external_data: Dict):
        """Draw external systems on left side"""
        
        y_start = 12
        for i, system in enumerate(external_data['components'][:3]):
            y_pos = y_start - (i * 3)
            
            # External system box
            ext_box = FancyBboxPatch((0.2, y_pos), 0.6, 2,
                                    boxstyle="round,pad=0.05",
                                    facecolor=self.colors['external'],
                                    edgecolor='#c62828',
                                    linewidth=1.5,
                                    linestyle='dashed')
            ax.add_patch(ext_box)
            
            # Label
            ax.text(0.1, y_pos + 1, system['name'],
                   ha='right', va='center', fontsize=7,
                   color='#c62828', rotation=90)
    
    def _draw_data_flows(self, ax, layers: Dict):
        """Draw arrows showing data flow between layers"""
        
        # Main vertical flow: Presentation -> Application -> Knowledge -> Acquisition -> Storage
        flow_x = 10
        
        # Presentation to Application
        if layers['presentation']['components'] and layers['application']['components']:
            ax.annotate('', xy=(flow_x, 11.5), xytext=(flow_x, 14.7),
                       arrowprops=dict(arrowstyle='-|>', color='#1976d2', linewidth=2.5))
            ax.text(flow_x + 0.5, 13, 'API Calls', fontsize=8, color='#1565c0')
        
        # Application to Knowledge
        if layers['application']['components'] and layers['knowledge']['components']:
            ax.annotate('', xy=(flow_x, 8), xytext=(flow_x, 11.2),
                       arrowprops=dict(arrowstyle='-|>', color='#388e3c', linewidth=2.5))
            ax.text(flow_x + 0.5, 9.5, 'Processing', fontsize=8, color='#2e7d32')
        
        # Knowledge to Acquisition
        if layers['knowledge']['components'] and layers['acquisition']['components']:
            ax.annotate('', xy=(flow_x, 4.5), xytext=(flow_x, 7.7),
                       arrowprops=dict(arrowstyle='-|>', color='#f57c00', linewidth=2.5))
            ax.text(flow_x + 0.5, 6, 'Data Flow', fontsize=8, color='#e65100')
        
        # All layers to Storage
        if layers['storage']['components']:
            # From Application
            if layers['application']['components']:
                ax.annotate('', xy=(8, 2), xytext=(8, 11.2),
                           arrowprops=dict(arrowstyle='-|>', color='#7b1fa2', linewidth=2, linestyle='dashed'))
            
            # From Knowledge
            if layers['knowledge']['components']:
                ax.annotate('', xy=(12, 2), xytext=(12, 7.7),
                           arrowprops=dict(arrowstyle='-|>', color='#7b1fa2', linewidth=2, linestyle='dashed'))
        
        # External systems to Application
        if layers['external']['components'] and layers['application']['components']:
            ax.annotate('', xy=(1.8, 12), xytext=(1, 12),
                       arrowprops=dict(arrowstyle='-|>', color='#c62828', linewidth=1.5, linestyle='dotted'))
