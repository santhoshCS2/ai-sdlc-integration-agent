from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os

# Mock key if not present (we expect it to fail with connection or auth error, not keyword argument error, if logic is correct)
# But we want to see if instantiation or invoke fails with argument error.

api_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-mock")
base_url = "https://openrouter.ai/api/v1"
model = "openai/gpt-4o"

print(f"Testing ChatOpenAI with model={model}")

try:
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7,
        max_tokens=100
    )
    
    print("LLM initialized.")
    # We won't actually hit the API if we don't have a valid key, but let's try to invoke.
    # If the error is in the library constructing the request params, it might happen before network or at the boundary.
    
    llm.invoke([HumanMessage(content="Hello")])
    print("Invoke successful (or failed with network error).")

except TypeError as e:
    print(f"Caught TypeError: {e}")
    if "reasoning_format" in str(e):
        print("CONFIRMED: reasoning_format caused the error.")
except Exception as e:
    print(f"Caught other error: {e}")
