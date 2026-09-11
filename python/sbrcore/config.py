# ============================================================================
# SBRCORE Configuration Manager
# Environment-based configuration for all services
# ============================================================================

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Centralized configuration manager for SBRCORE
    Loads from environment variables with sensible defaults
    """
    
    # =====================================================================
    # ENVIRONMENT & DEBUG
    # =====================================================================
    ENV = os.getenv('ENV_MODE', 'development')
    DEBUG = ENV == 'development'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # =====================================================================
    # DATABASE CONFIGURATION
    # =====================================================================
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/sbrcore'
    )
    DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', 20))
    DATABASE_ECHO = DEBUG
    
    # =====================================================================
    # AUTHENTICATION & SECURITY
    # =====================================================================
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    ENCRYPTION_SALT = os.getenv('ENCRYPTION_SALT', 'default-salt-change-in-production')
    
    # OAuth2 Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
    
    # =====================================================================
    # AI SERVICES - MULTI-ENGINE ROUTING
    # =====================================================================
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
    GROQ_TIMEOUT = int(os.getenv('GROQ_TIMEOUT', 30))
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', 30))
    
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')
    CLAUDE_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', 30))
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', 30))
    
    # Default AI engine for routing
    DEFAULT_AI_ENGINE = os.getenv('DEFAULT_AI_ENGINE', 'groq')
    
    # =====================================================================
    # ENVIRONMENTAL DATA APIs
    # =====================================================================
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NASA_API_KEY = os.getenv('NASA_API_KEY')
    AIRNOW_API_KEY = os.getenv('AIRNOW_API_KEY')
    
    # =====================================================================
    # AUDIO & VOICE SYNTHESIS
    # =====================================================================
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'default')
    
    # =====================================================================
    # VIDEO & VISUAL PROCESSING
    # =====================================================================
    LUMA_API_KEY = os.getenv('LUMA_API_KEY')
    NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')
    
    # =====================================================================
    # MAPPING & GEOSPATIAL
    # =====================================================================
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # =====================================================================
    # FIREBASE & CLOUD INFRASTRUCTURE
    # =====================================================================
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    
    # =====================================================================
    # GOOGLE CLOUD
    # =====================================================================
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # =====================================================================
    # APPLICATION SETTINGS
    # =====================================================================
    APP_NAME = os.getenv('APP_NAME', 'SBRCORE')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
    
    # =====================================================================
    # LOGGING & MONITORING
    # =====================================================================
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Safely get configuration value"""
        return getattr(cls, key, default)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENV == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENV == 'development'
