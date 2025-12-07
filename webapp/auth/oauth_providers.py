#!/usr/bin/env python3
"""
OAuth Provider Integration
Supports: Google, Twitter/X, GitHub, Apple
"""

import os
import requests
import secrets
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import json


class OAuthProvider:
    """Base class for OAuth providers"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str) -> str:
        """Get OAuth authorization URL"""
        raise NotImplementedError
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError


class GoogleOAuth(OAuthProvider):
    """Google OAuth provider"""
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        response.raise_for_status()
        data = response.json()
        return {
            'provider': 'google',
            'provider_id': data['id'],
            'email': data.get('email'),
            'name': data.get('name'),
            'username': data.get('email', '').split('@')[0],
            'avatar_url': data.get('picture'),
            'verified': data.get('verified_email', False)
        }


class TwitterOAuth(OAuthProvider):
    """Twitter/X OAuth 2.0 provider"""
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'tweet.read users.read offline.access',
            'state': state,
            'code_challenge': 'challenge',  # PKCE would be better
            'code_challenge_method': 'plain'
        }
        return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code_verifier': 'challenge'  # Should match code_challenge
        }
        response = requests.post('https://api.twitter.com/2/oauth2/token', data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://api.twitter.com/2/users/me?user.fields=profile_image_url,verified',
            headers=headers
        )
        response.raise_for_status()
        data = response.json().get('data', {})
        return {
            'provider': 'twitter',
            'provider_id': data['id'],
            'username': data.get('username'),
            'name': data.get('name'),
            'avatar_url': data.get('profile_image_url'),
            'verified': data.get('verified', False)
        }


class GitHubOAuth(OAuthProvider):
    """GitHub OAuth provider"""
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user:email',
            'state': state
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        headers = {'Accept': 'application/json'}
        response = requests.post('https://github.com/login/oauth/access_token', data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {'Authorization': f'token {access_token}'}
        response = requests.get('https://api.github.com/user', headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Get email
        email_response = requests.get('https://api.github.com/user/emails', headers=headers)
        email_data = email_response.json() if email_response.ok else []
        primary_email = next((e['email'] for e in email_data if e.get('primary')), data.get('email'))
        
        return {
            'provider': 'github',
            'provider_id': str(data['id']),
            'username': data.get('login'),
            'name': data.get('name'),
            'email': primary_email,
            'avatar_url': data.get('avatar_url'),
            'verified': True  # GitHub accounts are verified
        }


class AppleOAuth(OAuthProvider):
    """Apple Sign In provider (OAuth 2.0)"""
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'name email',
            'state': state,
            'response_mode': 'form_post'
        }
        return f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        # Apple requires JWT for token exchange - simplified here
        # In production, use proper JWT signing
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        response = requests.post('https://appleid.apple.com/auth/token', data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        # Apple provides user info in the initial token response
        # This is a placeholder - actual implementation needs JWT handling
        return {
            'provider': 'apple',
            'provider_id': 'apple_user',
            'email': None,  # Apple provides email in initial response
            'verified': True
        }


class OAuthManager:
    """Manages OAuth providers"""
    
    def __init__(self, base_dir=None):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize OAuth providers from environment variables"""
        redirect_base = os.getenv('OAUTH_REDIRECT_BASE', 'http://localhost:5002')
        
        # Google
        if os.getenv('GOOGLE_CLIENT_ID'):
            self.providers['google'] = GoogleOAuth(
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                redirect_uri=f"{redirect_base}/api/auth/google/callback"
            )
        
        # Twitter/X
        if os.getenv('TWITTER_CLIENT_ID'):
            self.providers['twitter'] = TwitterOAuth(
                client_id=os.getenv('TWITTER_CLIENT_ID'),
                client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
                redirect_uri=f"{redirect_base}/api/auth/twitter/callback"
            )
        
        # GitHub
        if os.getenv('GITHUB_CLIENT_ID'):
            self.providers['github'] = GitHubOAuth(
                client_id=os.getenv('GITHUB_CLIENT_ID'),
                client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
                redirect_uri=f"{redirect_base}/api/auth/github/callback"
            )
        
        # Apple
        if os.getenv('APPLE_CLIENT_ID'):
            self.providers['apple'] = AppleOAuth(
                client_id=os.getenv('APPLE_CLIENT_ID'),
                client_secret=os.getenv('APPLE_CLIENT_SECRET'),
                redirect_uri=f"{redirect_base}/api/auth/apple/callback"
            )
    
    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by name"""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> list:
        """Get list of available OAuth providers"""
        return list(self.providers.keys())

