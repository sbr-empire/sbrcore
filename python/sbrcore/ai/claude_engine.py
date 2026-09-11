# ============================================================================
# Claude Engine
# Anthropic Claude API support
# ============================================================================

from typing import Dict, Any, Optional
import httpx
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class ClaudeEngine:
    """
    Anthropic Claude API wrapper
    """
    
    API_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(
        self,
        api_key: str = Config.CLAUDE_API_KEY,
        model: str = Config.CLAUDE_MODEL,
        timeout: int = Config.CLAUDE_TIMEOUT
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
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
        Generate response using Claude API
        """
        payload = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [
                {
                    'role': 'user',
                    'content': f"{self._get_system_prompt(use_case)}\n\n{prompt}"
                }
            ],
            'temperature': temperature,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.API_URL,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API error: {response.text}")
                raise Exception(f"Claude API error: {response.status_code}")
            
            data = response.json()
            return data['content'][0]['text']
    
    def _get_system_prompt(self, use_case: str) -> str:
        prompts = {
            'translation': 'You are an expert in language translation with nuanced understanding.',
            'analysis': 'You are a brilliant analyst providing thorough insights.',
            'generation': 'You are a skilled writer creating exceptional content.',
            'general': 'You are a thoughtful and helpful AI assistant.'
        }
        return prompts.get(use_case, prompts['general'])
