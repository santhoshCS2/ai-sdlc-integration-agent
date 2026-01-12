from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.github_service import clone_repo, push_new_repo
from app.services.fix_service import fix_repo_code
from app.services.scan_parser import parse_scan_report
from app.database import get_db, CodeReview
from app.middleware.rate_limit import rate_limiter
from sqlalchemy.orm import Session
import tempfile, shutil, os, json, logging
from dotenv import load_dotenv

# Configure logging
if not logging.getLogger().hasHandlers():
    try:
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('app.log')
                ]
            ) 
        except (PermissionError, OSError):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
    except Exception as e:
        print(f"Logging setup failed: {e}")

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Automated Code Review & Code-Fix Agent",
        "description": "Clone repo, analyze scan report, fix issues, push to new repo",
        "endpoints": {
            "POST /review": "Submit repo_url and scan_report for automated fixing"
        },
        "output_format": {
            "updated_repo_link": "URL of fixed repository",
            "changes_summary": "List of file-wise fixes and optimizations"
        }
    }

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

@app.post("/review")
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
        repo_path = clone_repo(repo_url, tmp_dir)
        issues = parse_scan_report(report_text, report_bytes)
        
        if not issues:
            return {"updated_repo_link": repo_url, "change_report": []}

        changes = fix_repo_code(repo_path, issues)
        new_repo_url = push_new_repo(repo_path, repo_url, github_token)
        change_report = format_change_report(changes)

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
                logger.error(f"Database error: {e}")
                db.rollback()
        
        return {"updated_repo_link": new_repo_url, "change_report": change_report}

    except Exception as e:
        logger.error(f"Review failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if tmp_dir:
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Cleanup error: {e}")