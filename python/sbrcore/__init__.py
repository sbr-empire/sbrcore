# ============================================================================
# SBRCORE Package Initialization
# ============================================================================

from .config import Config
from .auth import JWTHandler, OAuthManager
from .database import DatabaseConnection
from .ai import AIRouter
from .ecommerce import ProductService, PaymentService
from .logging import get_logger

__all__ = [
    'Config',
    'JWTHandler',
    'OAuthManager',
    'DatabaseConnection',
    'AIRouter',
    'ProductService',
    'PaymentService',
    'get_logger'
]

__version__ = '1.0.0'
