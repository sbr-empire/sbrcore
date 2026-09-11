# ============================================================================
# JWT Token Handler
# Secure token generation and validation
# ============================================================================

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from functools import wraps
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class TokenExpiredException(Exception):
    """Token has expired"""
    pass

class InvalidTokenException(Exception):
    """Token is invalid"""
    pass

class JWTHandler:
    """
    Handles JWT token generation and validation
    Supports custom claims and expiration times
    """
    
    def __init__(
        self,
        secret_key: str = Config.JWT_SECRET_KEY,
        algorithm: str = Config.JWT_ALGORITHM,
        expiration_hours: int = Config.JWT_EXPIRATION_HOURS
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
    
    def generate_token(
        self,
        user_id: str,
        email: str,
        roles: list = None,
        additional_claims: Dict[str, Any] = None,
        expires_in_hours: Optional[int] = None
    ) -> str:
        """
        Generate JWT token with user information
        
        Args:
            user_id: Unique user identifier
            email: User email
            roles: List of user roles
            additional_claims: Extra claims to include
            expires_in_hours: Token expiration time
        
        Returns:
            Encoded JWT token
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'roles': roles or ['user'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours or self.expiration_hours),
            'jti': secrets.token_hex(16)  # JWT ID for revocation
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token generated for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode JWT token
        
        Args:
            token: JWT token to validate
        
        Returns:
            Decoded token payload
        
        Raises:
            TokenExpiredException: If token has expired
            InvalidTokenException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"Token validated for user: {payload.get('user_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token attempted: {token[:20]}...")
            raise TokenExpiredException("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise InvalidTokenException(f"Invalid token: {str(e)}")
    
    def refresh_token(self, token: str) -> str:
        """
        Generate a new token from an existing one
        
        Args:
            token: Existing JWT token
        
        Returns:
            New JWT token
        """
        try:
            payload = self.validate_token(token)
            # Remove expiration to use default
            payload.pop('exp', None)
            payload.pop('iat', None)
            
            return self.generate_token(
                user_id=payload['user_id'],
                email=payload['email'],
                roles=payload.get('roles'),
                additional_claims={k: v for k, v in payload.items() 
                                 if k not in ['user_id', 'email', 'roles', 'exp', 'iat']}
            )
        except TokenExpiredException:
            logger.warning("Cannot refresh expired token without bypass")
            raise
    
    def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from token
        
        Args:
            token: JWT token
        
        Returns:
            Dictionary with user info
        """
        payload = self.validate_token(token)
        return {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'roles': payload.get('roles', []),
            'issued_at': payload.get('iat'),
            'expires_at': payload.get('exp')
        }

def require_auth(roles: list = None):
    """
    Decorator to require JWT authentication on Flask routes
    
    Args:
        roles: Optional list of required roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Missing authorization header'}), 401
            
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
            
            jwt_handler = JWTHandler()
            try:
                payload = jwt_handler.validate_token(token)
                
                if roles and not any(role in payload.get('roles', []) for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                kwargs['user'] = payload
                return f(*args, **kwargs)
            
            except TokenExpiredException:
                return jsonify({'error': 'Token expired'}), 401
            except InvalidTokenException:
                return jsonify({'error': 'Invalid token'}), 401
        
        return decorated_function
    return decorator
