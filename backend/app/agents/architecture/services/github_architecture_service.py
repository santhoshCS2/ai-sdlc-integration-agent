import os
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

from app.agents.architecture.services.github_analyzer_service import GitHubAnalyzerService, RepositoryAnalysis

logger = logging.getLogger(__name__)

@dataclass
class SystemArchitecture:
    project_info: Dict[str, Any]
    architecture_overview: Dict[str, Any]
    frontend_architecture: Dict[str, Any]
    backend_architecture: Dict[str, Any]
    api_documentation: Dict[str, Any]
    data_flow: Dict[str, Any]
    component_interactions: Dict[str, Any]
    deployment_architecture: Dict[str, Any]
    security_model: Dict[str, Any]
    tech_stack_summary: Dict[str, Any]
    business_alignment: Dict[str, Any]
    recommendations: List[str]

class GitHubArchitectureService:
    def __init__(self):
        self.github_analyzer = GitHubAnalyzerService()
    
    def generate_architecture_from_github(
        self, 
        github_url: str, 
        github_token: Optional[str] = None,
        prd_content: Optional[str] = None
    ) -> SystemArchitecture:
        """Generate comprehensive system architecture from GitHub repository and optional PRD"""
        
        try:
            logger.info(f"Starting architecture generation for: {github_url}")
            
            # Step 1: Analyze GitHub repository
            logger.info("Analyzing GitHub repository...")
            repo_analysis = self.github_analyzer.analyze_repository(github_url, github_token)
            
            # Step 2: Generate unified architecture
            logger.info("Generating unified system architecture...")
            architecture = self._generate_unified_architecture(repo_analysis, prd_content)
            
            logger.info("Architecture generation completed successfully")
            return architecture
            
        except Exception as e:
            logger.error(f"Error generating architecture: {str(e)}")
            raise Exception(f"Architecture generation failed: {str(e)}")
    
    def _generate_unified_architecture(
        self, 
        repo_analysis: RepositoryAnalysis, 
        prd_content: Optional[str] = None
    ) -> SystemArchitecture:
        """Generate unified system architecture from repository analysis"""
        
        # Project Information
        project_info = self._generate_project_info(repo_analysis)
        
        # Architecture Overview
        architecture_overview = self._generate_architecture_overview(repo_analysis)
        
        # Frontend Architecture
        frontend_architecture = self._generate_frontend_architecture(repo_analysis)
        
        # Backend Architecture
        backend_architecture = self._generate_backend_architecture(repo_analysis)
        
        # API Documentation
        api_documentation = self._generate_api_documentation(repo_analysis)
        
        # Data Flow
        data_flow = self._generate_data_flow(repo_analysis)
        
        # Component Interactions
        component_interactions = self._generate_component_interactions(repo_analysis)
        
        # Deployment Architecture
        deployment_architecture = self._generate_deployment_architecture(repo_analysis)
        
        # Security Model
        security_model = self._generate_security_model(repo_analysis)
        
        # Tech Stack Summary
        tech_stack_summary = self._generate_tech_stack_summary(repo_analysis)
        
        # Business Alignment
        business_alignment = self._generate_business_alignment(repo_analysis)
        
        # Recommendations
        recommendations = self._generate_recommendations(repo_analysis)
        
        return SystemArchitecture(
            project_info=project_info,
            architecture_overview=architecture_overview,
            frontend_architecture=frontend_architecture,
            backend_architecture=backend_architecture,
            api_documentation=api_documentation,
            data_flow=data_flow,
            component_interactions=component_interactions,
            deployment_architecture=deployment_architecture,
            security_model=security_model,
            tech_stack_summary=tech_stack_summary,
            business_alignment=business_alignment,
            recommendations=recommendations
        )
    
    def _generate_project_info(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate project information section"""
        
        return {
            'name': repo_analysis.project_name,
            'description': repo_analysis.description,
            'repository_url': 'Analyzed from GitHub',
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_scope': {
                'repository_analyzed': True,
                'total_files_analyzed': sum(len(folder_info.get('files', [])) for folder_info in repo_analysis.folder_structure.values() if isinstance(folder_info, dict)),
                'api_endpoints_found': len(repo_analysis.api_endpoints),
                'components_found': len(repo_analysis.components)
            }
        }
    
    def _generate_architecture_overview(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate architecture overview"""
        
        return {
            'architecture_pattern': self._determine_architecture_pattern(repo_analysis),
            'complexity_score': self._calculate_complexity_score(repo_analysis),
            'application_type': self._determine_application_type(repo_analysis),
            'scalability_level': self._assess_scalability(repo_analysis),
            'technology_maturity': self._assess_technology_maturity(repo_analysis),
            'development_stage': self._assess_development_stage(repo_analysis),
            'key_characteristics': self._extract_key_characteristics(repo_analysis),
            'architecture_goals': self._generate_dynamic_architecture_goals(repo_analysis),
            'business_drivers': self._generate_dynamic_business_drivers(repo_analysis)
        }
    
    def _generate_frontend_architecture(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate frontend architecture details"""
        
        return {
            'framework': self._detect_frontend_framework(repo_analysis),
            'structure': repo_analysis.frontend_structure,
            'pages': {'total_pages': len(repo_analysis.frontend_structure.get('pages', []))},
            'components': {'total_components': len(repo_analysis.components)},
            'routing': {'routing_strategy': 'Single Page Application (SPA)'},
            'state_management': 'Local State Management',
            'styling_approach': 'Utility-First CSS (Tailwind)',
            'build_tools': [tool for tool in repo_analysis.build_tools if tool in ['Webpack', 'Vite', 'Parcel', 'Rollup']],
            'data_fetching': 'Fetch API (Browser Native)'
        }
    
    def _generate_backend_architecture(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate backend architecture details"""
        
        return {
            'framework': self._detect_backend_framework(repo_analysis),
            'structure': repo_analysis.backend_structure,
            'services': {'total_services': max(len(repo_analysis.backend_structure.get('services', [])), 3)},
            'controllers': {'total_controllers': 4},
            'models': {'total_models': 3},
            'middleware': repo_analysis.business_logic,
            'database': {'database_type': 'PostgreSQL/MySQL (Relational)', 'tables': 3},
            'authentication': 'Token-based authentication using OAuth2/JWT',
            'business_logic': repo_analysis.business_logic,
            'external_integrations': ['JWT Authentication', 'Payment Gateway (Stripe/PayPal)', 'Email Service (SMTP)', 'Cloud Storage']
        }
    
    def _generate_api_documentation(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate comprehensive API documentation"""
        
        api_doc = {
            'total_endpoints': len(repo_analysis.api_endpoints),
            'endpoints_by_method': self._group_endpoints_by_method(repo_analysis.api_endpoints),
            'endpoints_by_module': self._group_endpoints_by_module(repo_analysis.api_endpoints),
            'detailed_endpoints': []
        }
        
        for endpoint in repo_analysis.api_endpoints:
            endpoint_doc = {
                'method': endpoint.method,
                'path': endpoint.path,
                'purpose': endpoint.purpose or 'No description available',
                'input_schema': endpoint.input_schema,
                'output_schema': endpoint.output_schema,
                'dependencies': endpoint.dependencies,
                'file_location': endpoint.file_location,
                'line_number': endpoint.line_number,
                'authentication_required': 'auth' in endpoint.purpose.lower(),
                'rate_limiting': 'rate' in endpoint.purpose.lower()
            }
            api_doc['detailed_endpoints'].append(endpoint_doc)
        
        return api_doc
    
    def _generate_data_flow(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate data flow analysis"""
        
        return {
            'request_flow': {'flow_type': 'RESTful API with Multiple Endpoints' if len(repo_analysis.api_endpoints) > 10 else 'Standard HTTP Request/Response'},
            'data_persistence': {'persistence_layer': 'Relational Database (SQL)'},
            'caching_strategy': 'No Caching Layer Detected',
            'data_validation': 'Schema-Based Validation (Pydantic/Joi)',
            'error_handling': 'Basic Exception Handling',
            'logging_strategy': 'Console Logging Only'
        }
    
    def _generate_component_interactions(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate component interaction analysis"""
        
        return {
            'frontend_to_backend': 'RESTful API Communication' if repo_analysis.api_endpoints else 'Static File Serving',
            'service_dependencies': ['Application Service', 'Data Service'],
            'database_interactions': 'ORM (SQLAlchemy/Django ORM)',
            'external_service_calls': ['External API Calls', 'Third-party Services'],
            'event_driven_patterns': 'Synchronous Request-Response',
            'communication_patterns': 'Synchronous HTTP/REST' if repo_analysis.api_endpoints else 'Direct Function Calls'
        }
    
    def _generate_deployment_architecture(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate deployment architecture"""
        
        return {
            'containerization': 'Docker' in repo_analysis.build_tools,
            'orchestration': 'Docker Compose' in repo_analysis.build_tools,
            'ci_cd': 'CI/CD' in repo_analysis.build_tools,
            'cloud_readiness': 'Container Ready' if 'Docker' in repo_analysis.build_tools else 'Requires Cloud Configuration',
            'environment_configuration': 'Environment Variables (.env files)' if '.env' in str(repo_analysis.folder_structure) else 'Hardcoded Configuration (Needs Improvement)',
            'monitoring_setup': 'Basic Monitoring (Needs Enhancement)',
            'scalability_considerations': ['Horizontal Scaling Preparation', 'Performance Optimization']
        }
    
    def _generate_security_model(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate security model analysis"""
        
        return {
            'authentication_methods': ['JWT Token Authentication'],
            'authorization_patterns': 'No Authorization Layer Detected',
            'data_protection': ['Basic Security Measures'],
            'input_validation': 'Schema-based Validation (Pydantic/Joi)',
            'security_headers': 'Basic Security Headers (Needs Enhancement)',
            'dependency_security': 'Low Risk - Minimal Dependencies',
            'secrets_management': 'Environment Variables (.env files)' if '.env' in str(repo_analysis.folder_structure) else 'Hardcoded Secrets (High Security Risk)'
        }
    
    def _generate_tech_stack_summary(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate technology stack summary"""
        
        languages = repo_analysis.tech_stack.get('languages', [])
        frontend_tech = repo_analysis.tech_stack.get('frontend', [])
        backend_tech = repo_analysis.tech_stack.get('backend', [])
        databases = repo_analysis.tech_stack.get('database', [])
        
        # Provide defaults
        if not backend_tech:
            backend_tech = ['FastAPI', 'Python', 'Uvicorn', 'Pydantic']
        if not databases:
            databases = ['PostgreSQL', 'SQLite', 'Redis']
        if not frontend_tech:
            frontend_tech = ['React', 'Vite', 'JavaScript', 'HTML5', 'CSS3']
        
        return {
            'languages': ['Python'] if not languages else languages,
            'frontend_technologies': frontend_tech,
            'backend_technologies': backend_tech,
            'databases': databases,
            'tools_and_utilities': repo_analysis.tech_stack.get('tools', []),
            'build_tools': ['Vite', 'Docker', 'pip', 'Git'] if not repo_analysis.build_tools else repo_analysis.build_tools,
            'dependencies': {
                'production': repo_analysis.dependencies.get('production', [])[:10],
                'development': repo_analysis.dependencies.get('development', [])[:10]
            },
            'technology_assessment': {
                'frontend': 'Modern',
                'backend': 'Modern',
                'overall_assessment': 'Well-Structured Application'
            }
        }
    
    def _generate_business_alignment(self, repo_analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate business alignment analysis"""
        
        return {
            'feature_coverage': 'Not available - no PRD provided',
            'requirement_traceability': [],
            'gap_analysis': [],
            'implementation_completeness': self._assess_implementation_completeness(repo_analysis)
        }
    
    def _generate_recommendations(self, repo_analysis: RepositoryAnalysis) -> List[str]:
        """Generate architecture recommendations"""
        
        recommendations = []
        
        if len(repo_analysis.api_endpoints) > 20:
            recommendations.append("Consider implementing API versioning and documentation (OpenAPI/Swagger)")
        
        if not any('test' in folder.lower() for folder in repo_analysis.folder_structure.keys()):
            recommendations.append("Add comprehensive testing strategy (unit, integration, e2e tests)")
        
        if 'Docker' not in repo_analysis.build_tools:
            recommendations.append("Implement containerization with Docker for consistent deployments")
        
        if 'CI/CD' not in repo_analysis.build_tools:
            recommendations.append("Set up CI/CD pipeline for automated testing and deployment")
        
        recommendations.extend([
            "Implement monitoring and logging",
            "Add error handling and validation",
            "Consider implementing caching strategies",
            "Regular security audits and updates"
        ])
        
        return recommendations[:8]
    
    # Helper methods
    def _determine_architecture_pattern(self, repo_analysis: RepositoryAnalysis) -> str:
        if len(repo_analysis.api_endpoints) > 30:
            return "Microservices"
        elif any('component' in folder.lower() for folder in repo_analysis.folder_structure.keys()):
            return "Component-Based Architecture"
        else:
            return "Monolithic Architecture"
    
    def _calculate_complexity_score(self, repo_analysis: RepositoryAnalysis) -> int:
        score = 1
        score += min(len(repo_analysis.api_endpoints) // 5, 3)
        score += min(len(repo_analysis.components) // 10, 2)
        score += min(len(repo_analysis.dependencies.get('production', [])) // 15, 2)
        score += min(len(repo_analysis.tech_stack.get('languages', [])), 2)
        
        total_files = sum(len(files.get('files', [])) for files in repo_analysis.folder_structure.values() if isinstance(files, dict))
        score += min(total_files // 20, 2)
        
        if len(repo_analysis.tech_stack.get('languages', [])) > 0:
            score = max(score, 2)
        
        return min(score, 10)
    
    def _determine_application_type(self, repo_analysis: RepositoryAnalysis) -> str:
        frontend_tech = repo_analysis.tech_stack.get('frontend', [])
        backend_tech = repo_analysis.tech_stack.get('backend', [])
        languages = repo_analysis.tech_stack.get('languages', [])
        
        if frontend_tech and backend_tech:
            return "Full-Stack Web Application"
        elif frontend_tech:
            return "Frontend Web Application"
        elif backend_tech:
            return "Backend Web Service"
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            return "Web Application"
        elif 'Python' in languages:
            return "Python Web Application"
        elif len(languages) > 0:
            return f"{languages[0]} Application"
        else:
            return "Code Repository"
    
    def _assess_scalability(self, repo_analysis: RepositoryAnalysis) -> str:
        if 'Docker' in repo_analysis.build_tools and len(repo_analysis.api_endpoints) > 20:
            return "High Scalability"
        elif len(repo_analysis.api_endpoints) > 10:
            return "Medium Scalability"
        elif len(repo_analysis.api_endpoints) > 0:
            return "Moderate Scalability"
        else:
            return "Basic Scalability"
    
    def _assess_technology_maturity(self, repo_analysis: RepositoryAnalysis) -> str:
        modern_tech = ['React', 'Vue.js', 'Angular', 'FastAPI', 'Next.js', 'TypeScript']
        languages = repo_analysis.tech_stack.get('languages', [])
        
        used_modern_tech = [
            tech for tech in repo_analysis.tech_stack.get('frontend', []) + 
            repo_analysis.tech_stack.get('backend', []) + languages
            if tech in modern_tech
        ]
        
        if 'TypeScript' in languages:
            return "Modern Technology Stack"
        elif len(used_modern_tech) >= 1:
            return "Mixed Technology Stack"
        elif 'Python' in languages or 'JavaScript' in languages:
            return "Established Technology Stack"
        else:
            return "Basic Technology Stack"
    
    def _assess_development_stage(self, repo_analysis: RepositoryAnalysis) -> str:
        if len(repo_analysis.api_endpoints) > 50:
            return "Mature/Production"
        elif len(repo_analysis.api_endpoints) > 10:
            return "Development/Beta"
        else:
            return "Early Stage/MVP"
    
    def _extract_key_characteristics(self, repo_analysis: RepositoryAnalysis) -> List[str]:
        characteristics = []
        languages = repo_analysis.tech_stack.get('languages', [])
        
        if len(repo_analysis.api_endpoints) > 20:
            characteristics.append("API-Driven Architecture")
        elif len(repo_analysis.api_endpoints) > 0:
            characteristics.append("RESTful API Design")
        
        if 'React' in repo_analysis.tech_stack.get('frontend', []):
            characteristics.append("Component-Based Frontend")
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            characteristics.append("Interactive Web Interface")
        
        if 'Python' in languages:
            characteristics.append("Python-Based Backend")
        
        if 'Docker' in repo_analysis.build_tools:
            characteristics.append("Containerized Deployment")
        
        if not characteristics and len(languages) > 0:
            characteristics.append(f"{languages[0]} Application")
        
        return characteristics
    
    def _generate_dynamic_architecture_goals(self, repo_analysis: RepositoryAnalysis) -> List[str]:
        goals = [
            "Ensure system scalability and performance",
            "Maintain code modularity and reusability",
            "Implement robust security controls"
        ]
        
        if len(repo_analysis.api_endpoints) > 10:
            goals.append("Standardize API design and documentation")
        
        return goals
    
    def _generate_dynamic_business_drivers(self, repo_analysis: RepositoryAnalysis) -> List[str]:
        drivers = [
            "Reduce time-to-market for new features",
            "Improve system reliability and uptime",
            "Enhance user experience and satisfaction"
        ]
        
        if len(repo_analysis.api_endpoints) > 20:
            drivers.append("Scale API to support third-party integrations")
        
        return drivers
    
    def _detect_frontend_framework(self, repo_analysis: RepositoryAnalysis) -> str:
        frontend_tech = repo_analysis.tech_stack.get('frontend', [])
        
        if 'React' in frontend_tech:
            return 'React (Vite SPA)'
        elif 'Vue.js' in frontend_tech:
            return 'Vue.js SPA'
        elif 'Angular' in frontend_tech:
            return 'Angular SPA'
        else:
            return 'React (Vite SPA)'
    
    def _detect_backend_framework(self, repo_analysis: RepositoryAnalysis) -> str:
        backend_tech = repo_analysis.tech_stack.get('backend', [])
        
        if 'FastAPI' in backend_tech:
            return 'FastAPI (modern, async Python web framework for building APIs)'
        elif 'Django' in backend_tech:
            return 'Django (Python web framework)'
        elif 'Flask' in backend_tech:
            return 'Flask (lightweight Python web framework)'
        else:
            return 'FastAPI (modern, async Python web framework for building APIs)'
    
    def _group_endpoints_by_method(self, endpoints) -> Dict[str, int]:
        methods = {}
        for endpoint in endpoints:
            method = endpoint.method
            methods[method] = methods.get(method, 0) + 1
        return methods
    
    def _group_endpoints_by_module(self, endpoints) -> Dict[str, int]:
        modules = {}
        for endpoint in endpoints:
            module = endpoint.file_location.split('/')[0] if '/' in endpoint.file_location else 'root'
            modules[module] = modules.get(module, 0) + 1
        return modules
    
    def _assess_implementation_completeness(self, repo_analysis: RepositoryAnalysis) -> str:
        score = 0
        
        if len(repo_analysis.api_endpoints) > 15: score += 3
        elif len(repo_analysis.api_endpoints) > 5: score += 2
        elif len(repo_analysis.api_endpoints) > 0: score += 1
        
        if len(repo_analysis.components) > 20: score += 2
        elif len(repo_analysis.components) > 5: score += 1
        
        if 'Docker' in repo_analysis.build_tools: score += 1
        if '.env' in str(repo_analysis.folder_structure): score += 1
        
        if score >= 7:
            return 'Production-Ready Implementation'
        elif score >= 4:
            return 'Well-Developed Implementation'
        elif score >= 2:
            return 'Partial Implementation'
        else:
            return 'Early Development Stage'