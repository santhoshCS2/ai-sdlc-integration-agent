from app.services.llm import llm_service

async def fix_code_with_llm(original_code: str, issue_description: str, file_path: str) -> str:
    """Use AI to fix code issues."""
    system_prompt = f"You are an expert software engineer. Fix the following code issues in '{file_path}'. Output ONLY the complete fixed code without any explanation or markdown formatting."
    prompt = f"Original Code:\n```python\n{original_code}\n```\n\nIssues:\n{issue_description}\n\nFixed Code:"
    
    fixed_code = await llm_service.get_response(prompt, system_prompt)
    
    # Clean up markdown if AI included it
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
    elif "```" in fixed_code:
        fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
        
    return fixed_code
