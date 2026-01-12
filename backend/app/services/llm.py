from app.core.config import settings
import httpx
import json

class LLMService:
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        if settings.GROQ_API_KEY:
            print("LLMService: GROQ_API_KEY detected.")
        else:
            print("LLMService: GROQ_API_KEY NOT detected.")

    async def get_response(self, prompt: str, system_prompt: str = "You are a professional SDLC Agent assistant. Provide concise, expert-level advice."):
        if not settings.GROQ_API_KEY:
            return "Error: GROQ_API_KEY is not configured. Please add it to your .env file."

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 4096
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_data = response.json()
                    print(f"Groq API Error: {response.status_code} - {error_data}")
                    return f"I apologize, but I'm having trouble connecting to my intelligence core right now. (Error: {response.status_code})"
                    
        except Exception as e:
            print(f"LLM Connection Error: {e}")
            return "Connection error: Unable to reach the AI engine. Please check your internet connection and API key."

llm_service = LLMService()
