# ============================================================================
# Custom Exception Classes
# ============================================================================

class SBRException(Exception):
    """
    Base exception class for SBRCORE
    """
    def __init__(self, message: str, code: str = 'UNKNOWN_ERROR', status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(SBRException):
    """Raised when authentication fails"""
    def __init__(self, message: str = 'Authentication failed'):
        super().__init__(message, 'AUTH_ERROR', 401)

class AuthorizationError(SBRException):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = 'Insufficient permissions'):
        super().__init__(message, 'AUTH_FORBIDDEN', 403)

class ValidationError(SBRException):
    """Raised when input validation fails"""
    def __init__(self, message: str = 'Validation failed', details: dict = None):
        super().__init__(message, 'VALIDATION_ERROR', 422)
        self.details = details or {}

class NotFoundError(SBRException):
    """Raised when resource is not found"""
    def __init__(self, resource: str = 'Resource'):
        super().__init__(f'{resource} not found', 'NOT_FOUND', 404)

class ConflictError(SBRException):
    """Raised when resource already exists"""
    def __init__(self, message: str = 'Resource already exists'):
        super().__init__(message, 'CONFLICT', 409)

class RateLimitError(SBRException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = 'Rate limit exceeded', retry_after: int = 60):
        super().__init__(message, 'RATE_LIMITED', 429)
        self.retry_after = retry_after
