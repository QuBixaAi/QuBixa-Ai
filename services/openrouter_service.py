import os
import httpx
import json
from dotenv import load_dotenv
from utils.logger import logger_instance as logger

# Load environment variables
load_dotenv()

class OpenRouterService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        # Force the correct model
        self.default_model = "google/gemini-2.5-flash"
        
        # Validate API key on initialization
        if not self.api_key:
            logger.error("CRITICAL: OPENROUTER_API_KEY not found in environment variables!")
            logger.error("Please check your .env file")
        else:
            logger.info(f"OpenRouter service initialized with model: {self.default_model}")
            logger.info(f"API Key loaded: {self.api_key[:20]}...")  # Show first 20 chars only

    async def get_chat_completion(self, messages, model=None, stream=False):
        if not self.api_key:
            error_msg = "OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        model = model or self.default_model
        
        logger.info(f"Sending request to OpenRouter with model: {model}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://qubixa-ai.com",
            "X-Title": "Qubixa AI Platform",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "max_tokens": 4000  # Limit tokens to avoid credit issues
        }

        async with httpx.AsyncClient() as client:
            try:
                if stream:
                    logger.info(f"Streaming requested for model {model}")
                    return self.stream_chat_completion(messages, model)
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                logger.info(f"OpenRouter response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_detail = response.text
                    logger.error(f"OpenRouter error {response.status_code}: {error_detail}")
                    return f"Error: {response.status_code} - {error_detail}"
            except Exception as e:
                logger.error(f"OpenRouter exception: {str(e)}")
                return f"Error: {str(e)}"

    async def stream_chat_completion(self, messages, model=None):
        """Stream chat completion with proper async generator"""
        if not self.api_key:
            logger.error("OpenRouter API key not found")
            yield "Error: API key missing"
            return

        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://qubixa-ai.com",
            "X-Title": "Qubixa AI Platform",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "max_tokens": 4000  # Limit tokens
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                json_data = json.loads(data)
                                if "choices" in json_data:
                                    delta = json_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"Error: {str(e)}"

openrouter_service = OpenRouterService()
