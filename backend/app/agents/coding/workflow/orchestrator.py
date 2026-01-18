"""
Main orchestrator that coordinates all agents using LangGraph
"""

from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import os

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.agents.coding.agents.planner import PlannerAgent
from app.agents.coding.agents.github_cloner import GitHubClonerAgent
from app.agents.coding.agents.report_parser import ReportParserAgent
from app.agents.coding.agents.frontend_analyzer import FrontendAnalyzerAgent
from app.agents.coding.agents.backend_generator import BackendGeneratorAgent
from app.agents.coding.agents.integrator import IntegratorAgent
from app.agents.coding.agents.packager import PackagerAgent
from app.agents.coding.agents.github_publisher import GitHubPublisherAgent
from app.agents.coding.utils.logger import StreamlitLogger
from app.core.llm.llm_factory import LLMFactory
from app.core.llm.llm_with_fallback import LLMWithFallback

class ProjectState:
    """State object for the LangGraph workflow"""
    def __init__(self):
        self.project_config: Dict[str, Any] = {}
        self.project_spec: Optional[Dict[str, Any]] = None
        self.frontend_code: Optional[Dict[str, str]] = None
        self.backend_code: Optional[Dict[str, str]] = None
        self.integrated_project: Optional[str] = None
        self.zip_path: Optional[str] = None
        self.errors: list = []

class ProjectOrchestrator:
    """Orchestrates the entire project generation workflow"""
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[StreamlitLogger] = None):
        self.logger = logger or StreamlitLogger()
        # Use LLM with automatic fallback to Groq if OpenRouter fails
        self.llm = LLMWithFallback(api_key)
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm, self.logger)
        self.github_cloner = GitHubClonerAgent(self.llm, self.logger)
        self.report_parser = ReportParserAgent(self.llm, self.logger)
        self.frontend_analyzer = FrontendAnalyzerAgent(self.llm, self.logger)
        self.backend_generator = BackendGeneratorAgent(self.llm, self.logger)
        self.integrator = IntegratorAgent(self.llm, self.logger)
        self.packager = PackagerAgent(self.llm, self.logger)
        self.github_publisher = GitHubPublisherAgent(self.llm, self.logger)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("github_cloner", self._github_cloner_node)
        workflow.add_node("frontend_analyzer", self._frontend_analyzer_node)
        workflow.add_node("report_parser", self._report_parser_node)
        workflow.add_node("backend_generator", self._backend_generator_node)
        workflow.add_node("project_assembler", self._project_assembler_node)
        workflow.add_node("hardcode_remover", self._hardcode_remover_node)
        workflow.add_node("auth_flow_fixer", self._auth_flow_fixer_node)
        workflow.add_node("api_integrator", self._api_integrator_node)
        workflow.add_node("packager", self._packager_node)
        workflow.add_node("github_publisher", self._github_publisher_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "github_cloner")
        workflow.add_edge("github_cloner", "frontend_analyzer")
        workflow.add_edge("frontend_analyzer", "report_parser")
        workflow.add_edge("report_parser", "backend_generator")
        workflow.add_edge("backend_generator", "project_assembler")
        workflow.add_edge("project_assembler", "hardcode_remover")
        workflow.add_edge("hardcode_remover", "auth_flow_fixer")
        workflow.add_edge("auth_flow_fixer", "api_integrator")
        workflow.add_edge("api_integrator", "packager")
        workflow.add_edge("packager", "github_publisher")
        workflow.add_edge("github_publisher", END)
        
        return workflow.compile()
    
    def generate_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete project from config"""
        self.logger.log("🚀 Starting project generation workflow...")
        
        # Initialize state
        state = {
            "project_config": project_config,
            "project_spec": None,
            "frontend_code": None,
            "api_endpoints": None,
            "backend_code": None,
            "hardcode_analysis": None,
            "integrated_project": None,
            "zip_path": None,
            "errors": []
        }
        
        try:
            # Run workflow
            self.logger.log("🔄 Starting LLM-powered project generation workflow...")
            final_state = self.workflow.invoke(state)
            
            # Validate that we got the required content
            if not final_state.get("project_spec"):
                raise Exception("Project specification was not generated")
            if not final_state.get("frontend_code"):
                raise Exception("Frontend code was not cloned from GitHub and generation is disabled. Please provide a valid GitHub repository URL.")
            
            backend_code = final_state.get("backend_code", {})
            if not backend_code:
                raise Exception("Backend code was not generated. Check if Impact Analysis report contains clear backend specifications.")
            if not isinstance(backend_code, dict):
                raise Exception(f"Backend code has invalid format: {type(backend_code)}")
            if len(backend_code) < 1:
                raise Exception("Backend code is empty. Ensure Impact Analysis report contains API endpoints, data models, and file structure.")
            
            self.logger.log(f"✅ Generated {len(backend_code)} backend files")
            
            self.logger.log("✅ Project generation completed successfully with LLM-generated code!")
            
            return {
                "project_path": final_state.get("zip_path"),
                "project_directory": final_state.get("integrated_project"),
                "project_spec": final_state.get("project_spec"),
                "github_result": final_state.get("github_result"),
                "success": True
            }
        except Exception as e:
            error_msg = str(e)
            self.logger.log(f"❌ Error in workflow: {error_msg}", level="error")
            
            # Provide helpful tips based on error type
            if "Backend code" in error_msg:
                self.logger.log("💡 Tip: Ensure your Impact Analysis report contains:", level="error")
                self.logger.log("  - Clear API endpoint specifications (GET /api/..., POST /api/...)", level="error")
                self.logger.log("  - Data model definitions with fields and types", level="error")
                self.logger.log("  - Backend file structure and organization", level="error")
            elif "402" in error_msg or "credits" in error_msg.lower():
                self.logger.log("💡 Tip: Add credits to your OpenRouter account or use Groq API key", level="error")
            elif "401" in error_msg or "Invalid API" in error_msg:
                self.logger.log("💡 Tip: Check your API key in .env file", level="error")
            
            raise
    
    def _planner_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Planner agent node"""
        self.logger.log("📋 Planning project architecture...")
        spec = self.planner.create_spec(state["project_config"])
        return {**state, "project_spec": spec}
    
    def _github_cloner_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub cloner agent node"""
        github_url = state["project_config"].get("github_repo_url")
        if not github_url or github_url == "":
            self.logger.log("ℹ️ No GitHub URL provided, skipping clone.")
            return {**state, "frontend_code": None}
            
        self.logger.log("🔄 Cloning frontend code from GitHub...")
        frontend_code = self.github_cloner.clone_repo(state["project_config"])
        return {**state, "frontend_code": frontend_code}

    def _frontend_analyzer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Frontend analyzer agent node"""
        self.logger.log("🔍 Analyzing frontend code for API requirements...")
        frontend_analysis = self.frontend_analyzer.analyze(state.get("frontend_code", {}))
        return {**state, "frontend_analysis": frontend_analysis}

    def _report_parser_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Report parser agent node - MANDATORY for correct endpoint extraction"""
        self.logger.log("📄 Analyzing Impact Analysis report for API endpoints...")
        report_data = self.report_parser.read_report(state["project_config"])
        
        # Validate that report was successfully parsed
        if not report_data.get("content"):
            raise Exception("Impact Analysis report is required but could not be parsed")
        
        self.logger.log(f"✅ Successfully extracted {len(report_data.get('content', ''))} characters from report")
        return {**state, "report_data": report_data}
    
    def _backend_generator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Backend generator agent node - uses parsed report data for accurate endpoints"""
        self.logger.log("🔧 Generating backend code from analyzed Impact Analysis...")
        
        # Ensure report data is available
        if not state.get("report_data"):
            raise Exception("Report data is required for backend generation")
        
        backend_code = self.backend_generator.generate(
            state["project_spec"],
            state["project_config"]["backend_stack"],
            state["project_config"],
            state["report_data"],  # Pass analyzed report data
            state.get("frontend_analysis") # Pass frontend code analysis
        )
        return {**state, "backend_code": backend_code}
    
    def _project_assembler_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Project assembler node - creates initial structure"""
        self.logger.log("📁 Assembling project structure...")
        project_path = self.integrator.assemble_project(
            state["project_config"],
            state["frontend_code"],
            state["backend_code"]
        )
        return {**state, "integrated_project": project_path}
    
    def _hardcode_remover_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Hardcode remover node - functionalized"""
        self.logger.log("🔧 Analyzing and removing hardcoded elements from project...")
        project_path = Path(state["integrated_project"])
        frontend_dir = project_path / "frontend"
        backend_dir = project_path / "backend"
        
        results = {"frontend": {}, "backend": {}}
        
        if frontend_dir.exists():
            self.logger.log("  🎨 Cleaning frontend...")
            results["frontend"] = self.integrator.run_hardcode_remover(
                frontend_dir,
                state.get("project_spec", {}).get("api_endpoints", [])
            )
            
        if backend_dir.exists():
            self.logger.log("  🔧 Cleaning backend...")
            results["backend"] = self.integrator.run_hardcode_remover(
                backend_dir,
                state.get("project_spec", {}).get("api_endpoints", [])
            )
            
        return {**state, "hardcode_analysis": results}
    
    def _auth_flow_fixer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Auth flow fixer node"""
        self.logger.log("🔐 Fixing authentication flows...")
        frontend_dir = Path(state["integrated_project"]) / "frontend"
        
        if frontend_dir.exists():
            self.integrator.run_auth_fixer(frontend_dir)
            
        return state

    def _api_integrator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """API integrator node"""
        self.logger.log("🔗 Injecting API connections into frontend...")
        frontend_dir = Path(state["integrated_project"]) / "frontend"
        
        if frontend_dir.exists():
            self.integrator.run_api_integrator(
                frontend_dir,
                state["project_spec"],
                state["backend_code"]
            )
            
        # Finalize (README, Git, Docker)
        self.integrator.finalize(
            Path(state["integrated_project"]),
            state["project_config"],
            state["project_spec"]
        )
            
        return state
    
    def _packager_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Packager agent node"""
        self.logger.log("📦 Packaging project...")
        zip_path = self.packager.package(
            state["integrated_project"],
            state["project_config"]["project_name"]
        )
        return {**state, "zip_path": zip_path}
    
    def _github_publisher_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub publisher agent node"""
        self.logger.log("🐙 Publishing to GitHub...")
        github_result = self.github_publisher.publish(
            state["project_config"],
            state["integrated_project"]
        )
        return {**state, "github_result": github_result}

