from django.urls import re_path
from .views.websocket import OrderWebSocketConsumer

websocket_urlpatterns = [
    re_path(r'ws/admin/orders/$', OrderWebSocketConsumer.as_asgi()),
]
