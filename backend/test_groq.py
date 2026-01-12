import os
import sys
from groq import Groq
import httpx

print(f"Python version: {sys.version}")
print(f"Httpx version: {httpx.__version__}")

try:
    print("Attempting to initialize Groq client...")
    client = Groq(api_key="test_key")
    print("Success!")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
