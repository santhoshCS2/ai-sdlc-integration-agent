@echo off
echo ========================================
echo  AI SDLC Integration Agent - GitHub Push
echo ========================================

echo.
echo [1/6] Initializing Git repository...
git init

echo.
echo [2/6] Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/santhoshCS2/ai-sdlc-integration-agent.git

echo.
echo [3/6] Adding all files to staging...
git add .

echo.
echo [4/6] Creating initial commit...
git commit -m "Initial commit: AI-Powered SDLC Automation Platform

- Complete FastAPI backend with 7 AI agents
- React TypeScript frontend with modern UI
- Professional Testing Agent with LLM analysis
- Architecture, Security, Code Review agents
- GitHub integration and PDF generation
- Docker containerization support
- Comprehensive documentation"

echo.
echo [5/6] Setting main branch...
git branch -M main

echo.
echo [6/6] Pushing to GitHub...
git push -u origin main --force

echo.
echo ========================================
echo  ✅ Successfully pushed to GitHub!
echo  Repository: https://github.com/santhoshCS2/ai-sdlc-integration-agent
echo ========================================

pause