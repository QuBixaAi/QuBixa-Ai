import os
import httpx
import json
from dotenv import load_dotenv
from utils.logger import logger_instance as logger

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_content(self, prompt, model="gemini-2.0-flash-lite-preview"):
        if not self.api_key:
            logger.error("Gemini API key missing")
            return "Error: API key missing"

        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    logger.error(f"Gemini API Error: {response.text}")
                    return f"Error: {response.status_code}"
            except Exception as e:
                logger.error(f"Gemini generating exception: {str(e)}")
                return f"Error: {str(e)}"

gemini_service = GeminiService()
