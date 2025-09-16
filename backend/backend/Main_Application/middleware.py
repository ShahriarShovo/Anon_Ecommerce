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
            
            # Debug: Log session cookie setting
            print(f"🍪 Middleware: Setting session cookie: {request.session.session_key}")
        
        return response


class CORSHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add CORS headers for session cookies
    """
    
    def process_response(self, request, response):
        # Add CORS headers for credentials
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response
