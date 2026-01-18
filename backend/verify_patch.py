import functools
import sys
from unittest.mock import MagicMock

def strip_reasoning(kwargs):
    if "reasoning_format" in kwargs:
        kwargs.pop("reasoning_format")
    return kwargs

def create_patch(original_func):
    @functools.wraps(original_func)
    def patched_func(*args, **kwargs):
        return original_func(*args, **strip_reasoning(kwargs))
    return patched_func

def test_patch_logic():
    # Simulate the OpenAI structure
    class MockCompletions:
        def create(self, *args, **kwargs):
            if "reasoning_format" in kwargs or "reasoning_effort" in kwargs:
                raise TypeError(f"Completions.create() got an unexpected keyword argument '{list(kwargs.keys())[0]}'")
            return "Success"

    completions = MockCompletions()
    
    # Verify it fails without patch
    try:
        completions.create(prompt="hi", reasoning_format="parsed")
        print("FAILED: Did not raise TypeError for reasoning_format without patch")
    except TypeError as e:
        print(f"Verified: Original raises error for reasoning_format: {e}")

    try:
        completions.create(prompt="hi", reasoning_effort="high")
        print("FAILED: Did not raise TypeError for reasoning_effort without patch")
    except TypeError as e:
        print(f"Verified: Original raises error for reasoning_effort: {e}")

    # Apply patch
    MockCompletions.create = create_patch(MockCompletions.create)
    
    # Try again
    try:
        result = completions.create(prompt="hi", reasoning_format="parsed")
        print(f"SUCCESS: Patch worked for reasoning_format! Result: {result}")
        result = completions.create(prompt="hi", reasoning_effort="high")
        print(f"SUCCESS: Patch worked for reasoning_effort! Result: {result}")
    except TypeError as e:
        print(f"FAILURE: Patch did not work! Error: {e}")

if __name__ == "__main__":
    test_patch_logic()
    
    # Now check if we can import the actual OpenAI and see if our patch applies
    try:
        # We need to add the backend to path to import app.main
        sys.path.append(".")
        from app.main import patch_llm_reasoning
        patch_llm_reasoning()
        
        import openai.resources.chat.completions as chat_completions
        if "patched_func" in str(chat_completions.Completions.create):
            print("REAL SUCCESS: Actual OpenAI Completions.create is patched!")
        else:
            print("REAL FAILURE: Actual OpenAI Completions.create is NOT patched!")
    except Exception as e:
        print(f"Note: Could not verify actual OpenAI import (might not be installed or path issue): {e}")
