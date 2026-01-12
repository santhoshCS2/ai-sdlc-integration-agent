from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import traceback
import requests
import logging
from typing import Optional
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.agents.architecture.models.schemas import PDFGenerationRequest, PDFGenerationResponse
from app.agents.architecture.services.github_analyzer_service import GitHubAnalyzerService
from app.agents.architecture.services.github_architecture_service import GitHubArchitectureService
from app.agents.architecture.services.github_pdf_service import GitHubPDFService

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting System Architecture Agent API...")
    os.makedirs("generated_pdfs", exist_ok=True)
    yield
    # Shutdown
    logger.info("Shutting down System Architecture Agent API...")

# Initialize FastAPI app
app = FastAPI(
    title="System Architecture Agent API",
    description="API for generating system architecture PDFs from GitHub repositories",
    version="1.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT') == 'development' else None,
    redoc_url="/redoc" if os.getenv('ENVIRONMENT') == 'development' else None,
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]
)

# Configure CORS for production
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - only GitHub services needed

# Mount static files for PDF downloads
os.makedirs("generated_pdfs", exist_ok=True)
app.mount("/pdfs", StaticFiles(directory="generated_pdfs"), name="pdfs")


@app.get("/api")
async def api_root():
    """API Root endpoint"""
    return {
        "message": "System Architecture Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "generate_github_architecture": "/api/generate-github-architecture (POST)",
            "download": "/api/download/{filename} (GET)"
        }
    }


@app.get("/api/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Comprehensive health check endpoint"""
    try:
        # Check API keys
        groq_key = os.getenv('GROQ_API_KEY')
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # Check file system
        pdf_dir_exists = os.path.exists("generated_pdfs")
        
        health_status = {
            "status": "healthy",
            "service": "System Architecture Agent API",
            "version": "1.0.0",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "checks": {
                "groq_api_configured": bool(groq_key),
                "huggingface_api_configured": bool(hf_key),
                "pdf_directory_exists": pdf_dir_exists,
                "disk_space_available": True  # Could add actual disk space check
            }
        }
        
        # Determine overall health
        all_checks_pass = all(health_status["checks"].values())
        if not all_checks_pass:
            health_status["status"] = "degraded"
            
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/generate-github-architecture", response_model=PDFGenerationResponse)
@limiter.limit("3/minute")  # Rate limit: 3 requests per minute (GitHub cloning is resource intensive)
async def generate_github_architecture(
    request: Request,
    github_link: str = Form(..., min_length=10, max_length=500),
    github_token: str = Form("", min_length=0, max_length=200),  # Optional GitHub token
    prd_document: Optional[UploadFile] = File(None)
):
    """Generate comprehensive system architecture PDF from GitHub repository and optional PRD"""
    client_ip = get_remote_address(request)
    logger.info(f"GitHub architecture generation request from {client_ip} for repo: {github_link[:50]}...")
    
    try:
        # Validate GitHub URL
        if not ('github.com' in github_link or 'gitlab.com' in github_link):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid repository URL. Please provide a valid GitHub or GitLab URL."
            )
        
        # Process PRD document if provided
        prd_content = None
        if prd_document:
            # Security validations
            if prd_document.size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="PRD file size exceeds 10MB limit"
                )
            
            allowed_types = {
                'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain', 'text/markdown', 'application/json'
            }
            
            if prd_document.content_type not in allowed_types:
                logger.warning(f"Unsupported PRD file type: {prd_document.content_type}")
            
            try:
                file_content = await prd_document.read()
                # Don't decode here - let the document extractor handle it
                prd_content = None  # Will be set by document extraction
                logger.info(f"📝 PRD document received: {prd_document.filename} ({len(file_content)} bytes)")
                
                # Handle all document types using GitHubPDFService
                if (prd_document.content_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] or 
                    prd_document.filename.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.xls'))):
                    logger.info(f"📝 Document file detected: {prd_document.filename}, attempting text extraction...")
                    try:
                        github_pdf_service = GitHubPDFService()
                        # Save the file temporarily for extraction
                        import tempfile
                        file_extension = os.path.splitext(prd_document.filename)[1] or '.tmp'
                        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
                            temp_file.write(file_content)
                            temp_file_path = temp_file.name
                        
                        # Extract text using universal document reader
                        extracted_text = github_pdf_service.extract_text_from_file(temp_file_path)
                        if extracted_text and len(extracted_text.strip()) > 10:
                            prd_content = extracted_text
                            logger.info(f"✅ Document text extraction successful: {len(prd_content)} characters")
                        else:
                            logger.warning("⚠️ Document extraction yielded minimal content, using decoded fallback")
                        
                        # Clean up temp file
                        os.unlink(temp_file_path)
                    except Exception as doc_e:
                        logger.warning(f"⚠️ Document text extraction failed: {str(doc_e)}, using decoded content")
                
            except Exception as e:
                logger.error(f"Error processing PRD document: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not process PRD document. Please ensure it's a valid text file."
                )
        
        # Initialize GitHub architecture service
        logger.info("🔍 Initializing GitHub architecture analysis...")
        github_arch_service = GitHubArchitectureService()
        
        # Generate comprehensive architecture
        logger.info("📊 Analyzing repository and generating architecture...")
        try:
            print(f"🔍 Starting analysis for: {github_link}")
            print(f"🔑 Token provided: {bool(github_token)}")
            print(f"📄 PRD provided: {bool(prd_content)}")
            
            # Get repository analysis for AI-powered diagrams
            repo_analysis = github_arch_service.github_analyzer.analyze_repository(
                github_link, 
                github_token if github_token else None
            )
            
            architecture = github_arch_service.generate_architecture_from_github(
                github_url=github_link,
                github_token=github_token if github_token else None,
                prd_content=prd_content
            )
            
            print(f"✅ Architecture generated successfully")
            print(f"📊 API Endpoints: {architecture.api_documentation.get('total_endpoints', 0)}")
            components_count = architecture.frontend_architecture.get('components', {}).get('total_components', 0)
            services_count = architecture.backend_architecture.get('services', {}).get('total_services', 0)
            languages_count = len(architecture.tech_stack_summary.get('languages', []))
            
            print(f"🏗️ Components: {components_count}")
            print(f"🔧 Services: {services_count}")
            print(f"💻 Languages: {languages_count}")
        except Exception as e:
            error_msg = str(e)
            if "Repository cloning failed" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not access repository. Please check the URL and ensure it's public or provide a valid token. Error: {error_msg}"
                )
            elif "Authentication" in error_msg or "403" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Repository access denied. Please provide a valid GitHub token for private repositories."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Architecture analysis failed: {error_msg}"
                )
        
        # Generate professional PDF
        logger.info("📄 Generating comprehensive architecture PDF...")
        logger.info(f"📝 PRD content status: {'Provided' if prd_content else 'Not provided'}")
        if prd_content:
            logger.info(f"📝 PRD content length: {len(prd_content)} characters")
            logger.info(f"📝 PRD content sample: {prd_content[:300]}...")
        
        github_pdf_service = GitHubPDFService(output_dir="generated_pdfs")
        
        try:
            # Parse PRD content to extract product name and other details
            prd_analysis = None
            if prd_content:
                # Parse PRD content to extract structured information including product name
                prd_analysis = github_pdf_service.parse_prd_content(prd_content)
                logger.info(f"📝 PRD parsed - Product: {prd_analysis.get('product_name', 'Unknown')}")
                logger.info(f"📝 PRD features: {len(prd_analysis.get('features', []))}")
                logger.info(f"📝 PRD API endpoints: {len(prd_analysis.get('api_endpoints', []))}")
            
            pdf_path = github_pdf_service.generate_architecture_pdf(
                architecture=architecture,
                github_url=github_link,
                prd_included=prd_content is not None,
                repo_analysis=repo_analysis,
                prd_content=prd_content  # Pass original content for internal parsing
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF generation failed: {str(e)}"
            )
        
        # Get filename and URL
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/api/download/{pdf_filename}"
        
        # Prepare response
        response_data = {
            "success": True,
            "message": f"GitHub architecture analysis completed successfully. Repository analyzed with {architecture.project_info.get('analysis_scope', {}).get('total_files_analyzed', 0)} files.",
            "pdf_url": pdf_url,
            "pdf_filename": pdf_filename,
            "architecture_analysis": {
                "complexity_score": architecture.architecture_overview.get('complexity_score', 0),
                "application_type": architecture.architecture_overview.get('application_type', 'Unknown'),
                "architecture_pattern": architecture.architecture_overview.get('architecture_pattern', 'Unknown'),
                "scalability_level": architecture.architecture_overview.get('scalability_level', 'Unknown'),
                "technology_maturity": architecture.architecture_overview.get('technology_maturity', 'Unknown')
            },
            "analysis_summary": {
                "api_endpoints": architecture.api_documentation.get('total_endpoints', 0),
                "components": architecture.frontend_architecture.get('components', {}).get('total_components', 0),
                "services": architecture.backend_architecture.get('services', {}).get('total_services', 0),
                "languages": len(architecture.tech_stack_summary.get('languages', [])),
                "complexity": f"{architecture.architecture_overview.get('complexity_score', 0)}/10",
                "recommendations": len(architecture.recommendations) if hasattr(architecture, 'recommendations') and architecture.recommendations else 0,
                "architecture_pattern": architecture.architecture_overview.get('architecture_pattern', 'Unknown'),
                "application_type": architecture.architecture_overview.get('application_type', 'Unknown'),
                "scalability_level": architecture.architecture_overview.get('scalability_level', 'Unknown'),
                "technology_maturity": architecture.architecture_overview.get('technology_maturity', 'Unknown')
            }
        }
        
        logger.info(f"✅ GitHub architecture PDF generated successfully: {pdf_filename}")
        return PDFGenerationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in GitHub architecture generation: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during architecture analysis: {str(e)}"
        )


# Figma PDF generation endpoint removed - only GitHub architecture generation is supported


@app.get("/api/download/{filename}")
async def download_pdf(filename: str):
    """
    Download generated PDF file
    
    Args:
        filename: Name of the PDF file to download
        
    Returns:
        FileResponse with PDF file
    """
    file_path = os.path.join("generated_pdfs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )

# Mount frontend static files after all API routes
# Ensure the frontend directory exists relative to current working directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at {frontend_path}")


if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    # Production-ready server configuration
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.debug else 4
    )
