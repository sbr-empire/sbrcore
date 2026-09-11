# ============================================================================
# API Decorators
# Authentication, authorization, rate limiting, logging
# ============================================================================

from functools import wraps
from typing import List, Callable, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time

from ..auth import JWTHandler, PermissionManager
from ..logging import get_logger
from .errors import AuthenticationError, AuthorizationError, RateLimitError

logger = get_logger(__name__)

# Rate limiting storage
_rate_limit_store = defaultdict(lambda: {'requests': [], 'blocked_until': None})

def require_auth(f: Callable) -> Callable:
    """
    Decorator to require JWT authentication
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route(user):
            return f"Hello {user['email']}"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationError('Missing authorization header')
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            raise AuthenticationError('Invalid authorization header format')
        
        jwt_handler = JWTHandler()
        try:
            payload = jwt_handler.validate_token(token)
            kwargs['user'] = payload
            return f(*args, **kwargs)
        except Exception as e:
            raise AuthenticationError(str(e))
    
    return decorated_function

def require_permission(permissions: List[str] = None, require_all: bool = False):
    """
    Decorator to check user permissions
    
    Args:
        permissions: List of required permissions
        require_all: If True, user must have ALL permissions; if False, ANY permission
    
    Usage:
        @app.route('/admin')
        @require_permission(['admin_access', 'manage_system'])
        def admin_panel(user):
            return 'Admin panel'
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = kwargs.get('user')
            if not user:
                raise AuthenticationError('User not authenticated')
            
            if not permissions:
                return f(*args, **kwargs)
            
            user_roles = user.get('roles', [])
            
            if require_all:
                if not PermissionManager.has_all_permissions(user_roles, permissions):
                    raise AuthorizationError(f'Missing required permissions: {permissions}')
            else:
                if not PermissionManager.has_any_permission(user_roles, permissions):
                    raise AuthorizationError(f'Missing any of permissions: {permissions}')
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorator for rate limiting
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Usage:
        @app.route('/api/heavy')
        @rate_limit(max_requests=10, window_seconds=60)
        def heavy_operation():
            return 'Result'
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            client_id = request.remote_addr
            now = datetime.utcnow()
            
            # Check if currently blocked
            rate_data = _rate_limit_store[client_id]
            if rate_data['blocked_until'] and now < rate_data['blocked_until']:
                retry_after = int((rate_data['blocked_until'] - now).total_seconds())
                raise RateLimitError(f'Rate limited. Retry after {retry_after}s', retry_after)
            
            # Clean old requests
            cutoff_time = now - timedelta(seconds=window_seconds)
            rate_data['requests'] = [
                req_time for req_time in rate_data['requests']
                if req_time > cutoff_time
            ]
            
            # Check limit
            if len(rate_data['requests']) >= max_requests:
                rate_data['blocked_until'] = now + timedelta(seconds=window_seconds)
                raise RateLimitError(f'Rate limit exceeded: {max_requests} requests per {window_seconds}s')
            
            rate_data['requests'].append(now)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_request(f: Callable) -> Callable:
    """
    Decorator to log all API requests
    
    Usage:
        @app.route('/api/endpoint')
        @log_request
        def endpoint():
            return 'Response'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"| Status: 200 | Duration: {duration:.2f}s"
            )
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"API Request: {request.method} {request.path} "
                f"| Error: {str(e)} | Duration: {duration:.2f}s"
            )
            raise
    
    return decorated_function
