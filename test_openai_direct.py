import os
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-mock")
base_url = "https://openrouter.ai/api/v1"

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

print("Attempting to call client.chat.completions.create with reasoning_format...")

try:
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
        reasoning_format="auto" # Trying to trigger the error explicitly
    )
    print("Success (unexpected)")
except TypeError as e:
    print(f"Caught TypeError: {e}")
    if "reasoning_format" in str(e):
        print("CONFIRMED: passing reasoning_format causes TypeError.")
except Exception as e:
    print(f"Caught other error: {e}")
