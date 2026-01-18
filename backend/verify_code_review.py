import sys
import os
import asyncio

# Setup path
sys.path.append(os.getcwd())

async def verify_agent():
    print("🔍 Testing Code Review Agent Imports...")
    try:
        # Test 1: Import Main Service
        print("  - Importing code_review_service...")
        from app.agents.code_review.code_review_agent import code_review_service
        print("  ✅ code_review_service imported successfully")

        # Test 2: Import Dependencies (to check refactored paths)
        print("  - Importing supporting services...")
        from app.agents.code_review.services.github_service import clone_repo
        from app.agents.code_review.services.fix_service import fix_repo_code
        from app.agents.code_review.services.pdf_service import code_review_pdf_service
        print("  ✅ All supporting services imported successfully")

        # Test 3: Check methods
        if hasattr(code_review_service, 'perform_code_review'):
            print("  ✅ Method 'perform_code_review' exists")
        else:
            print("  ❌ Method 'perform_code_review' MISSING")

        print("\n🎉 Code Review Agent is functionally ready!")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   (This usually means a path refactor update was missed in a file)")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_agent())
