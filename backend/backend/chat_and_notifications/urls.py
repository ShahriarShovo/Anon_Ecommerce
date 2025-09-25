from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet,
    ConversationInboxView,
    MessageViewSet,
    MessageMarkReadView,
    ParticipantViewSet,
    OnlineStatusView
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'inbox', ConversationInboxView, basename='inbox')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'participants', ParticipantViewSet, basename='participant')

urlpatterns = [
    path('api/chat/', include(router.urls)),
    path('api/chat/online-status/', OnlineStatusView.as_view({'post': 'create', 'get': 'list'}), name='online-status'),
]
