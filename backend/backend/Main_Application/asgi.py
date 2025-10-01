"""
ASGI config for Main_Application project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens
    """
    async def __call__(self, scope, receive, send):
        # Get token from query parameters
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        if query_string:
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            token = params.get('token')
        
        # Authenticate user with JWT token
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)
                scope['user'] = user
                print(f"WebSocket authentication successful for user: {user.email}")
            except (InvalidToken, TokenError, KeyError) as e:
                print(f"WebSocket authentication failed: {e}")
                scope['user'] = AnonymousUser()
        else:
            print("No token provided for WebSocket connection")
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    async def get_user(self, user_id):
        """Get user by ID"""
        try:
            return await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

# Import chat routing after Django setup
from chat_and_notifications.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from orders.routing import websocket_urlpatterns as order_websocket_urlpatterns

# Combine all WebSocket URL patterns
all_websocket_urlpatterns = chat_websocket_urlpatterns + order_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        JWTAuthMiddleware(
            URLRouter(all_websocket_urlpatterns)
        )
    ),
})
