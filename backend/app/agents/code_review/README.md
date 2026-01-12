# Enhanced Code Review Agent — Backend (FastAPI)

## Features
- **Git Repository Processing**: Clone any public Git repository
- **Scan Report Analysis**: Parse JSON scan reports to identify code issues
- **AI-Powered Code Fixing**: Use OpenAI GPT to automatically fix identified issues
- **Intelligent Logic Enhancement**: Improve code quality and apply best practices
- **Repository Management**: Push fixed code to new GitHub repository
- **Diff Generation**: Generate detailed before/after code comparisons
- **Database Storage**: Store all review sessions with complete history
- **RESTful API**: Clean endpoints for integration

## What's Enhanced
- **Database Integration**: SQLAlchemy with SQLite for storing review history
- **Better Code Fixes**: Enhanced LLM prompts for superior code improvements
- **Proper Diff Generation**: Backup original files for accurate diff creation
- **Multiple Endpoints**: Get individual reviews, list all reviews
- **Enhanced Error Handling**: Robust error management throughout the pipeline
- **Improved Mock Mode**: Better mock fixes for testing without API keys

## API Endpoints

### POST /review
**Input:**
- `repo_url` (form field): Git repository URL
- `scan_report` (file, optional): JSON scan report

**Output:**
```json
{
  "id": 1,
  "original_repo_url": "https://github.com/user/repo",
  "updated_repo_url": "https://github.com/user/fixed-repo",
  "change_report": [
    {
      "file": "src/main.py",
      "issues_fixed": ["Missing error handling", "Unused imports"],
      "diff": "--- src/main.py\n+++ src/main.py\n..."
    }
  ],
  "changes_summary": "Fixed 3 files with 7 total issues",
  "created_at": "2024-01-01T12:00:00"
}
```

### GET /reviews/{review_id}
Get specific review by ID

### GET /reviews
List all reviews with summary information

## Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Test with Mock Mode:**
   Set `MOCK_MODE=true` in .env to test without API keys

## Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for code fixing
- `GITHUB_TOKEN`: GitHub token for repository operations
- `GITHUB_USER`: GitHub username
- `DATABASE_URL`: Database connection string (default: SQLite)
- `MOCK_MODE`: Enable mock mode for testing (true/false)
- `PUSH_ENABLED`: Enable GitHub push operations (true/false)

## Database
The system automatically creates a SQLite database (`code_reviews.db`) to store:
- Original and updated repository URLs
- Scan reports and fix summaries
- Complete diff content
- Timestamps and metadata

## Mock Mode
When `MOCK_MODE=true`, the system provides enhanced mock fixes:
- **Python**: Fixes print statements, common syntax issues
- **JavaScript**: Adds missing semicolons, basic formatting
- **General**: Applies generic improvements with comments

This allows full testing of the pipeline without requiring API keys.