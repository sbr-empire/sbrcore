# ============================================================================
# AI Router - Multi-Engine LLM Routing
# Routes requests to best available AI engine
# ============================================================================

from typing import Dict, List, Optional, Any
from enum import Enum
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class AIEngine(Enum):
    """Available AI engines"""
    GROQ = 'groq'
    OPENAI = 'openai'
    CLAUDE = 'claude'
    GEMINI = 'gemini'

class AIRouter:
    """
    Intelligent router for multi-LLM support
    Routes requests based on:
    - Use case (translation, analysis, generation, etc.)
    - Speed requirements
    - Cost optimization
    - Model availability
    """
    
    def __init__(self):
        self.primary_engine = Config.DEFAULT_AI_ENGINE
        self.engines = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """
        Initialize all available AI engines
        """
        try:
            if Config.GROQ_API_KEY:
                from .groq_engine import GroqEngine
                self.engines[AIEngine.GROQ] = GroqEngine()
                logger.info("✅ Groq engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq: {e}")
        
        try:
            if Config.OPENAI_API_KEY:
                from .openai_engine import OpenAIEngine
                self.engines[AIEngine.OPENAI] = OpenAIEngine()
                logger.info("✅ OpenAI engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")
        
        try:
            if Config.CLAUDE_API_KEY:
                from .claude_engine import ClaudeEngine
                self.engines[AIEngine.CLAUDE] = ClaudeEngine()
                logger.info("✅ Claude engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Claude: {e}")
        
        try:
            if Config.GEMINI_API_KEY:
                from .gemini_engine import GeminiEngine
                self.engines[AIEngine.GEMINI] = GeminiEngine()
                logger.info("✅ Gemini engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
    
    async def route_request(
        self,
        prompt: str,
        use_case: str = 'general',
        preferred_engine: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route request to appropriate AI engine
        
        Args:
            prompt: User prompt/query
            use_case: Type of request (translation, analysis, generation, etc.)
            preferred_engine: Specific engine to use
            **kwargs: Additional parameters for the engine
        
        Returns:
            Dictionary with response and metadata
        """
        # Determine which engine to use
        engine = self._select_engine(use_case, preferred_engine)
        
        if not engine:
            return {
                'error': 'No AI engines available',
                'status': 'failed'
            }
        
        try:
            logger.info(f"Routing request to {engine.__class__.__name__}")
            response = await engine.generate(
                prompt=prompt,
                use_case=use_case,
                **kwargs
            )
            
            return {
                'response': response,
                'engine': engine.__class__.__name__,
                'use_case': use_case,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"AI request failed: {str(e)}")
            return {
                'error': str(e),
                'engine': engine.__class__.__name__,
                'status': 'failed'
            }
    
    def _select_engine(self, use_case: str, preferred_engine: Optional[str] = None):
        """
        Select best engine based on use case
        """
        # If preferred engine specified, use it
        if preferred_engine:
            for engine_type, engine in self.engines.items():
                if engine_type.value == preferred_engine:
                    return engine
        
        # Route based on use case
        routing_rules = {
            'translation': AIEngine.GROQ,      # Fastest
            'analysis': AIEngine.CLAUDE,        # Most accurate
            'generation': AIEngine.OPENAI,      # Best quality
            'vision': AIEngine.GEMINI,          # Multimodal
            'general': AIEngine.GROQ,           # Default (fast)
        }
        
        selected_engine_type = routing_rules.get(use_case, AIEngine.GROQ)
        return self.engines.get(selected_engine_type)
    
    async def batch_process(
        self,
        prompts: List[str],
        use_case: str = 'general'
    ) -> List[Dict[str, Any]]:
        """
        Process multiple prompts in batch
        
        Args:
            prompts: List of prompts to process
            use_case: Type of request
        
        Returns:
            List of responses
        """
        import asyncio
        
        tasks = [
            self.route_request(prompt, use_case)
            for prompt in prompts
        ]
        
        results = await asyncio.gather(*tasks)
        logger.info(f"Batch processing completed: {len(results)} prompts")
        return results
    
    def get_available_engines(self) -> List[str]:
        """
        Get list of available engines
        """
        return [engine.value for engine in self.engines.keys()]
