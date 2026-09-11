# ============================================================================
# Gemini Engine
# Google Gemini API support (Multimodal)
# ============================================================================

from typing import Dict, Any, Optional, List
import httpx
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class GeminiEngine:
    """
    Google Gemini API wrapper with multimodal support
    """
    
    API_URL = "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
    
    def __init__(
        self,
        api_key: str = Config.GEMINI_API_KEY,
        model: str = Config.GEMINI_MODEL,
        timeout: int = Config.GEMINI_TIMEOUT
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
    
    async def generate(
        self,
        prompt: str,
        use_case: str = 'general',
        temperature: float = 0.7,
        max_tokens: int = 2048,
        images: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate response using Gemini API
        Supports text and image inputs (multimodal)
        """
        contents = []
        
        # Add text prompt
        contents.append({
            'text': prompt
        })
        
        # Add images if provided
        if images:
            for image_url in images:
                contents.append({
                    'inlineData': {
                        'mimeType': 'image/jpeg',
                        'data': await self._get_image_base64(image_url)
                    }
                })
        
        payload = {
            'contents': [
                {
                    'parts': contents
                }
            ],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
            }
        }
        
        url = f"{self.API_URL.format(model=self.model)}?key={self.api_key}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.text}")
                raise Exception(f"Gemini API error: {response.status_code}")
            
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
    
    async def _get_image_base64(self, image_url: str) -> str:
        """
        Download image and convert to base64
        """
        import base64
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            return base64.b64encode(response.content).decode()
