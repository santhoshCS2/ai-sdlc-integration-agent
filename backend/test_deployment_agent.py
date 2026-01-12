import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

from app.agents.deployment.deployment_agent import deployment_service

async def test_deployment_agent():
    print("Testing Deployment Agent...")
    
    # Mock data
    github_url = "https://github.com/dasarisanthosh86/test-project"
    architecture_context = """
    ## Architecture Overview
    - Frontend: React (Vite)
    - Backend: Python (FastAPI)
    - Database: PostgreSQL
    - Recommended Platform: Railway
    """
    
    try:
        result = await deployment_service.generate_deployment_strategy(
            github_url=github_url,
            architecture_context=architecture_context,
            github_token=os.getenv("GITHUB_TOKEN")
        )
        
        print(f"\n=== RAW RESULT ===\n{result}")
        
        if result['status'] == 'success':
            print(f"Predicted URL: {result.get('predicted_url')}")
            print(f"File ID: {result.get('file_id')}")
            if 'strategy_data' in result:
                print(f"Strategy Data Keys: {list(result['strategy_data'].keys())}")
            print("\nSUCCESS: Deployment Agent is working correctly!")
        else:
             print(f"\nFAILURE: Agent returned error: {result.get('message')}")
             
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deployment_agent())
