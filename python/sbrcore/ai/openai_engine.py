# ============================================================================
# OpenAI Engine
# GPT-4 and GPT-3.5 support
# ============================================================================

from typing import Dict, Any, Optional
import httpx
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class OpenAIEngine:
    """
    OpenAI API wrapper for GPT models
    """
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(
        self,
        api_key: str = Config.OPENAI_API_KEY,
        model: str = Config.OPENAI_MODEL,
        timeout: int = Config.OPENAI_TIMEOUT
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def generate(
        self,
        prompt: str,
        use_case: str = 'general',
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generate response using OpenAI API
        """
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self._get_system_prompt(use_case)},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': 0.9,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.API_URL,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")
            
            data = response.json()
            return data['choices'][0]['message']['content']
    
    def _get_system_prompt(self, use_case: str) -> str:
        prompts = {
            'translation': 'You are a professional translator with expertise in multiple languages.',
            'analysis': 'You are a senior analyst with deep domain expertise.',
            'generation': 'You are a world-class content creator.',
            'general': 'You are a highly intelligent AI assistant.'
        }
        return prompts.get(use_case, prompts['general'])
