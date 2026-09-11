# ============================================================================
# SBRCORE API Module
# Common decorators, utilities, and error handling
# ============================================================================

from .decorators import require_auth, require_permission, rate_limit, log_request
from .errors import (
    SBRException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError
)
from .utils import (
    generate_id,
    hash_password,
    verify_password,
    send_email,
    format_error_response,
    format_success_response,
    paginate_query
)

__all__ = [
    'require_auth',
    'require_permission',
    'rate_limit',
    'log_request',
    'SBRException',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'NotFoundError',
    'ConflictError',
    'RateLimitError',
    'generate_id',
    'hash_password',
    'verify_password',
    'send_email',
    'format_error_response',
    'format_success_response',
    'paginate_query'
]
