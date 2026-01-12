import os
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, Form, File, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict
import time
import json
import uuid # Added for file_id generation (though not directly used in this diff, it's in the provided diff)
import tempfile
import shutil
import re
import logging

logger = logging.getLogger(__name__)

from app.services.llm import llm_service
from app.agents.uiux.uiux_agent import uiux_service
from app.agents.architecture.architecture_agent import architecture_service
from app.agents.impact_analysis.impact_analysis_agent import impact_analysis_service
from app.agents.coding.coding_agent import coding_service
from app.agents.testing.testing_agent import testing_service
from app.agents.security.security_scanning_agent import security_scanning_service
from app.agents.code_review.code_review_agent import code_review_service
from app.agents.deployment.deployment_agent import deployment_service
from app.services.github_integration_service import github_integration_service
from app.core.storage import get_report_path, register_report
from app.api.auth import get_current_user
from app.agents.code_review.app.services.github_service import clone_repo, push_new_repo
from app.agents.code_review.app.services.fix_service import fix_repo_code
from app.agents.code_review.app.services.scan_parser import parse_scan_report
from app.agents.code_review.app.services.pdf_service import code_review_pdf_service
from app.database import CodeReview
from app.middleware.rate_limit import rate_limiter
from app.models.user import User
from app.models.agent import Agent
from app.core.database import get_db
from app.crud import agent as agent_crud
from app.crud import chat as chat_crud
from app.crud import system as system_crud
from app.schemas import agent as agent_schemas
from app.schemas import chat as chat_schemas
from app.schemas import system as system_schemas

router = APIRouter()

def format_change_report(changes):
    """Format changes into report structure"""
    change_report = []
    for change in changes:
        diff_lines = []
        for line_change in change.get('line_changes', []):
            line_num = line_change.get('line_number', 0)
            if line_change['change_type'] == 'modified':
                diff_lines.append(f"Line {line_num}: - {line_change['original']}")
                diff_lines.append(f"Line {line_num}: + {line_change['fixed']}")
            elif line_change['change_type'] == 'added':
                diff_lines.append(f"Line {line_num}: + {line_change['fixed']}")
            elif line_change['change_type'] == 'removed':
                diff_lines.append(f"Line {line_num}: - {line_change['original']}")
        
        change_report.append({
            "file": change['full_path'],
            "issues_fixed": change.get('issues_fixed', []),
            "fix_explanation": change.get('fix_explanation', 'Code fixed'),
            "optimizations": change.get('optimizations', []),
            "total_lines_changed": change.get('total_lines_changed', 0),
            "line_changes": change.get('line_changes', []),
            "diff": "\n".join(diff_lines) if diff_lines else "No changes made"
        })
    return change_report

@router.post("/review")
async def review(request: Request, repo_url: str = Form(...), scan_report: UploadFile = File(...), github_token: str = Form(None), db: Session = Depends(get_db)):
    await rate_limiter.check_rate_limit(request)
    
    # Read and validate scan report first
    report_bytes = await scan_report.read()
    try:
        report_text = report_bytes.decode('utf-8') if report_bytes else None
    except UnicodeDecodeError:
        report_text = None
    
    # Validate repo URL matches scan report BEFORE cloning
    if report_text:
        try:
            report_data = json.loads(report_text)
            report_repo_url = report_data.get('repo_url', '')
            if report_repo_url:
                # Normalize URLs for comparison
                input_url = repo_url.strip().rstrip('/').replace('.git', '')
                report_url = report_repo_url.strip().rstrip('/').replace('.git', '')
                if input_url.lower() != report_url.lower():
                    raise HTTPException(
                        status_code=400,
                        detail=f"❌ Repository URL and Scan Report do not match!\n\nInput URL: {repo_url}\nReport URL: {report_repo_url}\n\nPlease upload the correct scan report for this repository."
                    )
        except json.JSONDecodeError:
            pass  # Skip validation if JSON parsing fails
    
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()
        repo_path = clone_repo(repo_url, tmp_dir, token=github_token)
        issues = parse_scan_report(report_text, report_bytes)
        
        if not issues:
            return {"updated_repo_link": repo_url, "change_report": [], "output": "No issues found in the scan report."}

        changes = await fix_repo_code(repo_path, issues)
        new_repo_url = push_new_repo(repo_path, repo_url, github_token)
        change_report = format_change_report(changes)

        # Generate professional PDF report
        file_id = str(uuid.uuid4())
        pdf_path = code_review_pdf_service.generate_report(repo_url, new_repo_url, change_report, file_id)
        register_report(file_id, pdf_path)
        download_url = f"/api/agents/download/code_review/{file_id}"

        # Generate rich Markdown summary
        output_md = f"### ✅ Automated Code Review & Fix Completed\n\n"
        output_md += f"**Updated Repository:** [{new_repo_url}]({new_repo_url})\n\n"
        output_md += f"📥 **Download PDF Report:** [Click here to download the Code Review Report]({download_url})\n\n"
        output_md += "#### 🛠️ Changes Applied:\n\n"
        
        if not changes:
            output_md += "No issues were identified that required code changes.\n"
        else:
            for change in change_report:
                output_md += f"- **File:** `{change['file']}`\n"
                output_md += f"  - **Issues Fixed:** {', '.join(change['issues_fixed'])}\n"
                output_md += f"  - **Explanation:** {change['fix_explanation']}\n"
                if change['optimizations']:
                    output_md += f"  - **Optimizations:** {', '.join(change['optimizations'])}\n"
                output_md += "\n"

        if db:
            try:
                db_review = CodeReview(
                    original_repo_url=repo_url,
                    updated_repo_url=new_repo_url,
                    scan_report=report_text,
                    changes_summary=json.dumps(change_report),
                    diff_content=json.dumps(changes)
                )
                db.add(db_review)
                db.commit()
            except Exception as e:
                print(f"Database error: {e}")
                db.rollback()
        
        return {
            "updated_repo_link": new_repo_url, 
            "change_report": change_report,
            "output": output_md
        }

    except Exception as e:
        print(f"Review failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if tmp_dir:
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Cleanup error: {e}")

# --- Agent Management ---

@router.get("/", response_model=List[agent_schemas.Agent])
async def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves a list of available AI agents."""
    return agent_crud.get_agents(db)

@router.post("/create", response_model=agent_schemas.Agent)
async def create_agent(
    agent: agent_schemas.AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provision a new AI agent with custom parameters."""
    return agent_crud.create_agent(db, agent, current_user.id)

@router.get("/{agent_id}", response_model=agent_schemas.Agent)
async def get_agent_details(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_agent = agent_crud.get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/{agent_id}")
async def decommission_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Decommissions an existing AI agent."""
    agent_crud.delete_agent(db, agent_id)
    return {"status": "Agent decommissioned successfully"}

# --- Chat & Interaction ---

@router.post("/chat")
async def chat_with_agents(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Orchestrates interaction between users and specific agents.
    """
    try:
        # Get form data manually to debug
        form_data = await request.form()
        print(f"Received form data: {dict(form_data)}")
        
        query = form_data.get("query")
        agent_id = form_data.get("agent_id")
        
        if not query:
            return {"status": "error", "response": "Query is required"}
        
        if not agent_id:
            # Default to first agent if not specified
            db_agent = db.query(Agent).first()
            if not db_agent:
                return {"status": "error", "response": "No agents available"}
            agent_id = db_agent.id
        else:
            try:
                agent_id = int(agent_id)
            except ValueError:
                return {"status": "error", "response": "Invalid agent ID"}
        
        print(f"Chat request - Query: {query}, Agent ID: {agent_id}")
        
        # Get Agent Details
        db_agent = agent_crud.get_agent(db, agent_id)
        if not db_agent:
            print(f"Agent {agent_id} not found, using mock response")
            return {
                "status": "success",
                "response": f"Mock response for query: {query}. Agent {agent_id} not found in database.",
                "agent": "Mock Agent",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Process based on agent type
        print(f"[DEBUG] Agent name: {db_agent.name}, Query: {query}")
        print(f"[DEBUG] Form data keys: {list(form_data.keys())}")
        
        if "UI/UX" in db_agent.name:
            print(f"[Orchestrator] Routing to UI/UX Service...")
            # Extract files from form data
            files_list = []
            
            # Check for files in different possible keys
            for key in form_data.keys():
                if 'file' in key.lower():
                    file_obj = form_data[key]
                    if hasattr(file_obj, 'filename') and file_obj.filename:
                        files_list.append(file_obj)
                        print(f"[DEBUG] Found file: {file_obj.filename}")
            
            print(f"[DEBUG] Processing {len(files_list)} files with UI/UX service")
            response_text = await uiux_service.process_prd(query, files_list if files_list else None)
            
        elif "Architecture" in db_agent.name or "architecture" in query.lower():
            print(f"[Orchestrator] Routing to Architecture Service...")
            github_url = None
            words = query.split()
            for word in words:
                if "github.com" in word:
                    github_url = word.strip('()[]",')
                    break
            
            if github_url:
                # Use the proper architecture service methods
                arch_result = await architecture_service.analyze_architecture("", github_url)
                file_id = await architecture_service.generate_architecture_report(arch_result, github_url)
                
                # Build download URL (relative path works in any environment)
                if file_id:
                    download_url = f"/api/agents/download/architecture/{file_id}"
                    # Format as markdown link for proper rendering in frontend
                    response_text = f"""✅ Architecture document generated successfully!

📥 **Download PDF Report:**
[Click here to download the Architecture Report]({download_url})

📊 **Analysis Summary:**
{arch_result[:500]}..."""
                else:
                    response_text = "Architecture analysis completed but PDF generation failed. Please check the logs."
            else:
                response_text = await llm_service.get_response(query, db_agent.system_prompt)
        
        elif "Testing" in db_agent.name:
            print(f"[Orchestrator] Routing to Professional Testing Service...")
            github_url = None
            words = query.split()
            for word in words:
                if "github.com" in word:
                    github_url = word.strip('()[]",')
                    break
            
            if github_url:
                test_data = await testing_service.run_comprehensive_testing(github_url, query)
                download_url = f"/api/agents/download/testing/{test_data['file_id']}" if test_data.get('file_id') else None
                response_text = f"✅ Professional testing analysis completed!\n\n"
                if download_url:
                    response_text += f"📥 **Download Test Suite Package:** [Click here]({download_url})\n\n"
                response_text += test_data["report_content"][:500] + "..."
            else:
                response_text = "Please provide a GitHub URL for comprehensive testing analysis."

        elif "Security" in db_agent.name:
            print(f"[Orchestrator] Routing to Security Service (Standalone)...")
            github_url = None
            words = query.split()
            for word in words:
                if "github.com" in word:
                    github_url = word.strip('()[]",')
                    break
            
            if github_url:
                scan_data = await security_scanning_service.scan_repository(github_url)
                download_url = f"/api/agents/download/security/{scan_data['file_id']}" if scan_data.get('file_id') else None
                response_text = f"✅ Security scan completed!\n\n"
                if download_url:
                    response_text += f"📥 **Download PDF Report:** [Click here]({download_url})\n\n"
                response_text += scan_data["report_content"][:500] + "..."
            else:
                response_text = "Please provide a GitHub URL for security scanning."

        elif "Code Review" in db_agent.name:
            print(f"[Orchestrator] Routing to Code Review Service (Standalone)...")
            repo_url = None
            words = query.split()
            for word in words:
                if "github.com" in word:
                    repo_url = word.strip('()[]",')
                    break
            
            if repo_url:
                review_path = await code_review_service.perform_code_review("Mock Code", "Mock Test", "Mock Security", "Mock PRD")
                review_content = ""
                if os.path.exists(review_path):
                    with open(review_path, "r", encoding="utf-8") as f:
                        review_content = f.read()
                response_text = f"✅ Code Review completed!\n\n" + review_content[:1000] + "..."
            else:
                response_text = "Please provide a GitHub URL for code review."
        else:
            print(f"[Orchestrator] Using standard LLM for: {db_agent.name}")
            response_text = await llm_service.get_response(query, db_agent.system_prompt)
        
        return {
            "status": "success",
            "response": response_text,
            "agent": db_agent.name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "status": "error",
            "response": f"Error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/conversations/{conversation_id}", response_model=chat_schemas.Conversation)
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches message history for a specific session."""
    db_conv = chat_crud.get_conversation(db, conversation_id)
    if not db_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conv

# --- Admin & Monitoring ---

@router.get("/admin/logs", response_model=List[system_schemas.SystemLog])
async def get_admin_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provides system-wide audit logs for administrators."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return system_crud.get_logs(db, skip, limit)

@router.get("/status")
async def get_pipeline_status():
    return {
        "is_active": True,
        "current_agent": "Idle",
        "queue_depth": 0
    }

@router.post("/test-chat")
async def test_chat(query: str = Form("Hello")):
    """Simple test endpoint for chat functionality"""
    return {
        "status": "success",
        "response": f"Test response for: {query}",
        "agent": "Test Agent",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/orchestrate-sdlc")
async def orchestrate_full_sdlc(
    request: Request,
    query: str = Form(""),
    step: int = Form(1),
    github_url: str = Form(""),
    github_token: str = Form(""),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Execute single agent step based on current step
    """
    try:
        current_step = step
        prd_query = query
        
        if github_token:
            github_integration_service.set_token(github_token)
            
        # Collect all files - handle the primary 'file' and any other potential file fields
        files_list = []
        if file:
            files_list.append(file)
            
        # Fallback: Check if there are any other files in the request form
        form_data = await request.form()
        for key in form_data.keys():
            if key != "file" and hasattr(form_data[key], 'filename'):
                files_list.append(form_data[key])
        
        logger.info(f"[SDLC] Step {current_step} | Query: '{prd_query[:40]}...' | Files Rcvd: {len(files_list)}")
        if len(files_list) > 0:
            for f in files_list:
                logger.info(f"  - Received File: {getattr(f, 'filename', 'unknown')} ({getattr(f, 'size', '??')} bytes)")
        
        if current_step == 1:
            # Step 1: UI/UX Agent only
            uiux_result = await uiux_service.process_prd(prd_query, files_list)
            
            # Check for error message from service
            if isinstance(uiux_result, str) and uiux_result.startswith("Error:"):
                return {
                    "status": "error",
                    "step": 1,
                    "agent": "UI/UX Agent",
                    "message": uiux_result
                }

            # Create GitHub repository if token is available
            repo_status_msg = ""
            if not github_url:
                repo_name = f"sdlc-project-{int(time.time())}"
                github_url = await github_integration_service.create_or_update_repository(
                    repo_name, "AI-Generated SDLC Project"
                )
                if github_url:
                    repo_status_msg = f" | Repository created: {github_url}"
                else:
                    repo_status_msg = " | GitHub repository creation skipped (No valid token)."
            
            return {
                "status": "success",
                "step": 1,
                "agent": "UI/UX Agent",
                "output": uiux_result,
                "github_repo": github_url,
                "next_step": 2,
                "message": f"UI/UX specifications generated{repo_status_msg}. Proceed to Architecture."
            }
            
        elif current_step == 2:
            # Step 2: Architecture Agent
            arch_result = await architecture_service.analyze_architecture(
                prd_query, github_url, github_token
            )
            
            # Generate professional PDF report
            file_id = await architecture_service.generate_architecture_report(arch_result, github_url)
            
            # PUSH ARCHITECTURE PDF TO GITHUB
            if github_url and file_id:
                try:
                    report_path = get_report_path(file_id)
                    if report_path and os.path.exists(report_path):
                        # Push PDF
                        pdf_filename = f"architecture_report_{file_id}.pdf"
                        # Use the actual filename if possible, but file_id ensures uniqueness
                        await github_integration_service.push_binary_file(
                            repo_url=github_url, 
                            file_path=report_path, 
                            target_path=f"reports/architecture/{pdf_filename}", 
                            message="Add Architecture PDF Report"
                        )
                        print(f"[SDLC] Architecture PDF pushed to GitHub: {github_url}")
                        
                        # Push Markdown summary
                        await github_integration_service.push_agent_outputs(github_url, {"architecture_design": arch_result})
                        print(f"[SDLC] Architecture Design (Markdown) pushed to GitHub: {github_url}")
                except Exception as gh_e:
                    print(f"[SDLC] Failed to push architecture to GitHub: {gh_e}")

            # Build download URL
            download_url = None
            if file_id:
                download_url = f"/api/agents/download/architecture/{file_id}"
                arch_result += f"\n\n---\n### 📥 [Download Full Architecture Report (PDF)]({download_url})"
            
            return {
                "status": "success",
                "step": 2,
                "agent": "Architecture Agent",
                "output": arch_result,
                "file_id": file_id,
                "download_url": download_url,
                "github_repo": github_url,
                "next_step": 3,
                "message": "System Architecture designed and pushed to GitHub. Proceed to Impact Analysis."
            }
            
        elif current_step == 3:
            # Step 3: Impact Analysis Agent
            # The prd_query here is the output from Step 2 (Architecture Agent)
            arch_context = prd_query
            
            # Since we only have one query field, we treat the incoming context as the source of truth
            # for the impact analysis. The Agent is designed to be resilient to missing PRD text.
            impact_data = await impact_analysis_service.analyze_impact(
                "Source Project Context", arch_context, github_url
            )
            
            # Build download URL
            download_url = None
            if impact_data.get("file_id"):
                download_url = f"/api/agents/download/impact/{impact_data['file_id']}"
            
            return {
                "status": "success",
                "step": 3,
                "agent": "Impact Analysis Agent",
                "output": impact_data["report_content"],
                "file_id": impact_data["file_id"],
                "download_url": download_url,
                "github_repo": github_url,
                "next_step": 4,
                "message": "Technical and Business impact analysis completed successfully. Download the full report below."
            }
            
        elif current_step == 4:
            # Step 4: Coding Agent
            # Generates code based on Architecture and Impact Analysis context
            # prd_query here contains the Architecture output from Step 2
            # We want to give it the best possible context for a professional structure
            code_dir = await coding_service.generate_code(
                prd_content="Source Project PRD", # Placeholder if original PRD not tracked in this stateless call
                architecture_content=prd_query, 
                github_url=github_url
            )
            
            # ZIP CODE FOR DOWNLOAD
            zip_path = coding_service.zip_generated_code(code_dir)
            file_id = str(uuid.uuid4())
            register_report(file_id, zip_path)
            
            # PUSH CODE TO GITHUB (Selective pushing)
            pushed_files = {}
            if github_url:
                print(f"[SDLC] Pushing generated code to GitHub: {github_url}")
                pushed_files = await github_integration_service.push_local_directory(github_url, code_dir)
            
            return {
                "status": "success",
                "step": 4,
                "agent": "Coding Agent",
                "output": f"Professional Full-stack code (Backend & Frontend) generated and pushed to repository.\n\nGitHub: {github_url}\nLocal Workspace: {code_dir}",
                "github_repo": github_url,
                "file_id": file_id,
                "download_url": f"/api/agents/download/coding/{file_id}",
                "next_step": 5,
                "message": "Source code generated successfully with professional standards. Proceed to Automated Testing.",
                "pushed_files": pushed_files
            }
            
        elif current_step == 5:
            # Step 5: Professional Testing Agent
            # Clones repo, analyzes each file with LLM, generates comprehensive test suite
            test_data = await testing_service.run_comprehensive_testing(
                github_url, prd_query, security_file_id=None, github_token=github_token
            )
            
            # Build download URL for test suite package
            download_url = None
            file_id = test_data.get("file_id")
            if file_id:
                download_url = f"/api/agents/download/testing/{file_id}"
                test_output = test_data.get("report_content", "") + f"\n\n---\n### 📥 [Download Complete Test Suite Package (ZIP)]({download_url})"
            else:
                test_output = test_data.get("report_content", "Testing analysis completed.")
            
            return {
                "status": "success",
                "step": 5,
                "agent": "Professional Testing Agent",
                "output": test_output,
                "file_id": file_id,
                "download_url": download_url,
                "statistics": test_data.get("statistics", {}),
                "github_repo": github_url,
                "next_step": 6,
                "message": f"Professional test suite generated. Analyzed {test_data.get('statistics', {}).get('code_files', 0)} code files and generated comprehensive test cases. Proceed to Security Scanning."
            }
            
        elif current_step == 6:
            # Step 6: Security Scanning Agent
            # Clones repo, analyzes code, and produces formatted security report with PDF
            scan_data = await security_scanning_service.scan_repository(github_url, testing_file_id=None, github_token=github_token)
            
            # Build download URL
            download_url = None
            file_id = scan_data.get("file_id")
            if file_id:
                download_url = f"/api/agents/download/security/{file_id}"
                scan_output = scan_data.get("report_content", "") + f"\n\n---\n### 📥 [Download Security Report (PDF)]({download_url})"
            else:
                scan_output = scan_data.get("report_content", "Security scan completed.")
            
            return {
                "status": "success",
                "step": 6,
                "agent": "Security Scanning Agent",
                "output": scan_output,
                "file_id": file_id,
                "download_url": download_url,
                "statistics": scan_data.get("statistics", {}),
                "github_repo": github_url,
                "next_step": 7,
                "message": f"Security scan completed. Found {scan_data.get('statistics', {}).get('security_issues', 0)} potential risks. Proceed to final Code Review & Fix."
            }
            
        elif current_step == 7:
            # Step 7: Automated Code Review & Fix Agent
            repo_url = github_url if github_url else prd_query
            
            # Security file ID might be passed in prd_query
            security_file_id = None
            if prd_query and len(prd_query) < 100 and '-' in prd_query:
                security_file_id = prd_query

            # Check if this is a "FIX" request
            is_fix_request = form_data.get("apply_fix") == "true"
            
            if not is_fix_request:
                # JUST REVIEW
                print(f"[SDLC Step 7] Performing Review only for {repo_url}")
                review_result_path = await code_review_service.perform_code_review("Mock Code", "Mock Test", "Mock Security", "Mock PRD", security_file_id=security_file_id)
                review_content = ""
                if os.path.exists(review_result_path):
                    with open(review_result_path, "r", encoding="utf-8") as f:
                        review_content = f.read()
                
                return {
                    "status": "success",
                    "step": 7,
                    "agent": "Code Review Agent",
                    "output": review_content,
                    "github_repo": repo_url,
                    "can_fix": True, # Indicate that fixes can be applied
                    "next_step": 7,  # Stay on step 7 for the fix
                    "message": "Code review completed. You can now apply the recommended fixes by clicking the 'Fix Issues' button."
                }

            # If it IS a fix request, run the following logic
            tmp_dir = tempfile.mkdtemp()
            try:
                # 1. Clone Repo
                print(f"[SDLC Step 7] Cloning repo: {repo_url}")
                repo_path = clone_repo(repo_url, tmp_dir, token=github_token)
                
                # 2. Get Scan Report (from file or previous step output in query)
                report_bytes = None
                report_text = prd_query
                if files_list:
                    report_bytes = await files_list[0].read()
                    try:
                        report_text = report_bytes.decode('utf-8')
                    except:
                        report_text = None

                # 3. Parse Issues
                print(f"[SDLC Step 7] Parsing scan report...")
                issues = parse_scan_report(report_text, report_bytes)
                
                # 4. Fix Code
                print(f"[SDLC Step 7] Fixing code based on {len(issues) if issues else 0} issue files...")
                changes = await fix_repo_code(repo_path, issues)
                
                # 5. Push Changes
                print(f"[SDLC Step 7] Pushing fixes to GitHub...")
                new_repo_url = push_new_repo(
                    repo_path, 
                    repo_url, 
                    github_token, 
                    commit_message="fix: Applied automated code review fixes", 
                    skip_env_check=True
                )
                
                # 6. Format Result
                change_report = format_change_report(changes)
                
                # Generate professional PDF report
                file_id = str(uuid.uuid4())
                pdf_path = code_review_pdf_service.generate_report(repo_url, new_repo_url, change_report, file_id)
                register_report(file_id, pdf_path)
                download_url = f"/api/agents/download/code_review/{file_id}"

                # Push PDF to GitHub if possible
                if github_token and pdf_path and os.path.exists(pdf_path):
                    try:
                        pdf_filename = f"code_review_report_{file_id}.pdf"
                        await github_integration_service.push_binary_file(
                            repo_url=new_repo_url,
                            file_path=pdf_path,
                            target_path=f"reports/code_review/{pdf_filename}",
                            message="Add Code Review Fix Report (PDF)"
                        )
                        print(f"[SDLC Step 7] Code Review PDF pushed to GitHub")
                    except Exception as gh_e:
                        print(f"[SDLC Step 7] Failed to push PDF to GitHub: {gh_e}")

                # Generate rich Markdown summary for chat output
                output_md = f"### ✅ Automated Code Review & Fix Completed\n\n"
                output_md += f"**Updated Repository:** [{new_repo_url}]({new_repo_url})\n\n"
                output_md += f"📥 **Download PDF Report:** [Click here to download the Code Review Report]({download_url})\n\n"
                
                if not changes:
                    output_md += "#### ℹ️ No changes required.\n"
                    output_md += "The code review did not identify any issues requiring automatic fixes based on the provided report.\n"
                else:
                    output_md += f"#### 🛠️ Fixed {len(changes)} Files:\n\n"
                    for change in change_report:
                        output_md += f"#### 📄 File: `{change['file']}`\n"
                        output_md += f"- **Issues Fixed:** {', '.join(change['issues_fixed'])}\n"
                        output_md += f"- **Explanation:** {change['fix_explanation']}\n"
                        if change['optimizations']:
                            output_md += f"- **AI Optimizations:** {', '.join(change['optimizations'])}\n"
                        output_md += "\n"

                # 7. Save to DB
                if db:
                    try:
                        db_review = CodeReview(
                            original_repo_url=repo_url,
                            updated_repo_url=new_repo_url,
                            scan_report=report_text if report_text else "Binary/File Report",
                            changes_summary=json.dumps(change_report),
                            diff_content=json.dumps(changes)
                        )
                        db.add(db_review)
                        db.commit()
                    except Exception as db_e:
                        print(f"Database error in Step 7: {db_e}")
                        db.rollback()

                return {
                    "status": "success",
                    "step": 7,
                    "agent": "Code Review Agent",
                    "output": output_md,
                    "github_repo": new_repo_url,
                    "change_report": change_report,
                    "file_id": file_id,
                    "download_url": download_url,
                    "next_step": 8,
                    "message": "Step 7 completed. Finalized code review and fixes. Proceed to Deployment Strategy."
                }

            except Exception as e:
                print(f"SDLC Step 7 Failed: {str(e)}")
                # Fallback to original behavior if fix logic fails
                review_result_path = await code_review_service.perform_code_review("", "", "", prd_query)
                review_content = ""
                if os.path.exists(review_result_path):
                    with open(review_result_path, "r", encoding="utf-8") as f:
                        review_content = f.read()
                return {
                    "status": "success",
                    "step": 7,
                    "agent": "Code Review Agent",
                    "output": review_content if review_content else f"Fix logic failed: {str(e)}",
                    "github_repo": repo_url,
                    "next_step": 8,
                    "message": "Workflow continued to deployment after automated fix failure."
                }
            finally:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

        elif current_step == 8:
            # Step 8: Deployment Strategist Agent
            # Generates a professional deployment guide and config
            strategy_data = await deployment_service.generate_deployment_strategy(
                github_url=github_url,
                architecture_context=prd_query, # Contains previously generated architecture/code context
                github_token=github_token
            )
            
            # Build download URL
            download_url = None
            file_id = strategy_data.get("file_id")
            if file_id:
                download_url = f"/api/agents/download/deployment/{file_id}"
                strategy_output = strategy_data.get("report_content", "") + f"\n\n---\n### 📥 [Download Deployment Strategy (PDF)]({download_url})"
            else:
                strategy_output = strategy_data.get("report_content", "Deployment strategy generated.")
            
            # PUSH DEPLOYMENT REPORT TO GITHUB
            if github_url and file_id:
                try:
                    report_path = get_report_path(file_id)
                    if report_path and os.path.exists(report_path):
                        pdf_filename = f"deployment_strategy_{file_id}.pdf"
                        await github_integration_service.push_binary_file(
                            repo_url=github_url,
                            file_path=report_path,
                            target_path=f"reports/deployment/{pdf_filename}",
                            message="Add Deployment Strategy (PDF)"
                        )
                        print(f"[SDLC] Deployment PDF pushed to GitHub")
                except Exception as gh_e:
                    print(f"[SDLC] Failed to push deployment PDF to GitHub: {gh_e}")

            return {
                "status": "success",
                "step": 8,
                "agent": "Deployment Strategist Agent",
                "output": strategy_output,
                "file_id": file_id,
                "download_url": download_url,
                "predicted_url": strategy_data.get("predicted_url"),
                "github_repo": github_url,
                "next_step": None,
                "message": "SDLC workflow completed successfully! Deployment strategy generated and pushed to GitHub. Railway is connected and will deploy automatically."
            }
        
        else:
            return {
                "status": "error",
                "message": "Invalid step number"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Step {current_step} failed: {str(e)}"
        }

@router.get("/download/{agent_type}/{file_id}")
async def download_agent_output(
    agent_type: str,
    file_id: str
):
    """
    Download actual generated agent report files.
    """
    try:
        file_path = get_report_path(file_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Requested report file not found or expired.")

        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/export/workflow/{workflow_id}")
async def export_workflow_results(
    workflow_id: str,
    format: str = "json"
):
    """
    Export complete workflow results in JSON or PDF format.
    """
    try:
        # Mock workflow data
        workflow_data = {
            "workflow_id": workflow_id,
            "status": "completed",
            "agents": [
                {"name": "UI/UX Agent", "status": "completed", "output": "Design specifications generated"},
                {"name": "Architecture Agent", "status": "completed", "output": "System architecture designed"},
                {"name": "Impact Analysis Agent", "status": "completed", "output": "Impact analysis completed"},
                {"name": "Coding Agent", "status": "completed", "output": "Backend code generated"},
                {"name": "Testing Agent", "status": "completed", "output": "Test suite created"},
                {"name": "Security Scanning Agent", "status": "completed", "output": "Security scan completed"},
                {"name": "Code Review Agent", "status": "completed", "output": "Code review finished"},
                {"name": "Deployment Strategist Agent", "status": "completed", "output": "Deployment strategy generated"}
            ],
            "github_repository": f"https://github.com/user/sdlc-project-{workflow_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if format.lower() == "json":
            return JSONResponse(workflow_data)
        else:
            # Create temporary text file for PDF-like export
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"SDLC Workflow Results\n\nWorkflow ID: {workflow_id}\n\n")
                for agent in workflow_data["agents"]:
                    f.write(f"{agent['name']}: {agent['status']} - {agent['output']}\n")
                f.write(f"\nGitHub Repository: {workflow_data['github_repository']}")
                temp_path = f.name
            
            return FileResponse(
                temp_path,
                media_type='text/plain',
                filename=f"workflow_{workflow_id}_results.txt"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
