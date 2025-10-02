from django.urls import re_path
from .views import ChatConsumer, AdminConsumer
from .consumers.contact_websocket_consumer import ContactWebSocketConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/admin/inbox/$', AdminConsumer.as_asgi()),
    re_path(r'ws/admin/contacts/$', ContactWebSocketConsumer.as_asgi()),
]
