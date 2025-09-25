from django.urls import re_path
from .views import ChatConsumer, AdminConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/admin/inbox/$', AdminConsumer.as_asgi()),
]
