"""
Custom Middleware
================

Custom middleware for handling session cookies and CORS.
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SessionCookieMiddleware(MiddlewareMixin):
    """
    Middleware to ensure session cookies are properly set
    """
    
    def process_request(self, request):
        # Ensure session is created if it doesn't exist
        if not request.session.session_key:
            request.session.create()
        return None
    
    def process_response(self, request, response):
        # Add session cookie headers for cross-origin requests
        if hasattr(request, 'session') and request.session.session_key:
            # Set session cookie with proper attributes
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                request.session.session_key,
                max_age=settings.SESSION_COOKIE_AGE,
                domain=settings.SESSION_COOKIE_DOMAIN,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE
            )
        
        return response


class CORSHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add CORS headers for session cookies
    """
    
    def process_response(self, request, response):
        # Add CORS headers for credentials
        response['Access-Control-Allow-Credentials'] = 'true'
        origin = request.META.get('HTTP_ORIGIN')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        # Add session cookie headers
        if hasattr(request, 'session') and request.session.session_key:
            response['Access-Control-Expose-Headers'] = 'Set-Cookie'
        
        return response
