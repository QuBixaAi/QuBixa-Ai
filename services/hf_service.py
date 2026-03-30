import os
import httpx
import json
from dotenv import load_dotenv
from utils.logger import logger_instance as logger

# Load environment variables
load_dotenv()

class HFService:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models"
        self.model = "sentence-transformers/all-MiniLM-L6-v2"

    async def get_embeddings(self, text):
        if not self.api_key:
            logger.error("HuggingFace API key missing")
            return []

        url = f"{self.api_url}/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": [text]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                if response.status_code == 200:
                    embeddings = response.json()
                    return embeddings[0]
                else:
                    logger.error(f"HuggingFace API Error: {response.text}")
                    return []
            except Exception as e:
                logger.error(f"HuggingFace embedding exception: {str(e)}")
                return []

hf_service = HFService()
