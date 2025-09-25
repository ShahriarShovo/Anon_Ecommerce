"""
ASGI configuration for chat system.
This file is specifically for WebSocket/async functionality.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

# Import routing after Django setup
from chat_and_notifications.routing import websocket_urlpatterns

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using token
    """
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if token:
            # Authenticate user with token
            from django.contrib.auth import get_user_model
            from rest_framework.authtoken.models import Token
            
            User = get_user_model()
            try:
                token_obj = Token.objects.get(key=token)
                scope['user'] = token_obj.user
            except Token.DoesNotExist:
                scope['user'] = None
        else:
            scope['user'] = None
        
        return await super().__call__(scope, receive, send)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
