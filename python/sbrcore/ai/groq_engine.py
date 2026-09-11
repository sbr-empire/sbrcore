# ============================================================================
# Groq AI Engine
# Ultra-fast LLM inference
# ============================================================================

from typing import Dict, Any, Optional
import httpx
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class GroqEngine:
    """
    Groq API wrapper for fastest LLM inference
    """
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(
        self,
        api_key: str = Config.GROQ_API_KEY,
        model: str = Config.GROQ_MODEL,
        timeout: int = Config.GROQ_TIMEOUT
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
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Generate response using Groq API
        
        Args:
            prompt: Input prompt
            use_case: Use case for optimization
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
        
        Returns:
            Generated text
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
                logger.error(f"Groq API error: {response.text}")
                raise Exception(f"Groq API error: {response.status_code}")
            
            data = response.json()
            return data['choices'][0]['message']['content']
    
    def _get_system_prompt(self, use_case: str) -> str:
        """
        Get optimized system prompt based on use case
        """
        prompts = {
            'translation': 'You are an expert translator. Translate accurately and naturally.',
            'analysis': 'You are an expert analyst. Provide deep insights and detailed analysis.',
            'generation': 'You are a creative writer. Generate high-quality, engaging content.',
            'general': 'You are a helpful AI assistant. Answer questions clearly and accurately.'
        }
        return prompts.get(use_case, prompts['general'])
