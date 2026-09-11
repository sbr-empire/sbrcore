# ============================================================================
# OAuth2 Manager
# Handle OAuth2 authentication with multiple providers
# ============================================================================

import httpx
from typing import Dict, Optional, Any
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class OAuthManager:
    """
    Manages OAuth2 authentication with various providers
    Currently supports: Google, GitHub, Microsoft
    """
    
    # OAuth2 Endpoints
    PROVIDERS = {
        'google': {
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'userinfo_url': 'https://openidconnect.googleapis.com/v1/userinfo'
        },
        'github': {
            'auth_url': 'https://github.com/login/oauth/authorize',
            'token_url': 'https://github.com/login/oauth/access_token',
            'userinfo_url': 'https://api.github.com/user'
        },
        'microsoft': {
            'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'userinfo_url': 'https://graph.microsoft.com/v1.0/me'
        }
    }
    
    def __init__(self, provider: str = 'google'):
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        self.provider = provider
        self.config = self.PROVIDERS[provider]
        logger.info(f"OAuthManager initialized for {provider}")
    
    def get_authorization_url(self, state: str, scopes: list = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            state: CSRF protection token
            scopes: List of requested scopes
        
        Returns:
            Authorization URL
        """
        if self.provider == 'google':
            client_id = Config.GOOGLE_CLIENT_ID
            redirect_uri = Config.GOOGLE_REDIRECT_URI
            default_scopes = ['openid', 'email', 'profile']
        else:
            raise NotImplementedError(f"OAuth provider {self.provider} not yet implemented")
        
        scope_str = ' '.join(scopes or default_scopes)
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope_str,
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.config['auth_url']}?{query_string}"
        
        logger.debug(f"Authorization URL generated for {self.provider}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth provider
        
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        if self.provider == 'google':
            client_id = Config.GOOGLE_CLIENT_ID
            client_secret = Config.GOOGLE_CLIENT_SECRET
            redirect_uri = Config.GOOGLE_REDIRECT_URI
        else:
            raise NotImplementedError(f"OAuth provider {self.provider} not yet implemented")
        
        payload = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.config['token_url'], data=payload)
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise Exception(f"Token exchange failed: {response.status_code}")
            
            token_data = response.json()
            logger.info(f"Token obtained for {self.provider}")
            return token_data
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user information from OAuth provider
        
        Args:
            access_token: OAuth access token
        
        Returns:
            User information dictionary
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.config['userinfo_url'], headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get user info: {response.text}")
                raise Exception(f"Failed to get user info: {response.status_code}")
            
            user_info = response.json()
            
            # Normalize user info
            normalized = {
                'provider': self.provider,
                'email': user_info.get('email'),
                'name': user_info.get('name', user_info.get('login')),
                'picture': user_info.get('picture', user_info.get('avatar_url')),
                'provider_id': user_info.get('sub', user_info.get('id')),
                'raw': user_info
            }
            
            logger.info(f"User info fetched: {normalized['email']}")
            return normalized
    
    async def authenticate(self, code: str) -> Dict[str, Any]:
        """
        Complete OAuth2 authentication flow
        
        Args:
            code: Authorization code from OAuth provider
        
        Returns:
            Token data and user information
        """
        token_data = await self.exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        user_info = await self.get_user_info(access_token)
        
        return {
            'tokens': token_data,
            'user': user_info
        }
