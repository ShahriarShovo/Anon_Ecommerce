from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet,
    ConversationInboxView,
    MessageViewSet,
    MessageMarkReadView,
    ParticipantViewSet,
    OnlineStatusView,
    NotificationViewSet,
    NotificationPublicView,
    DiscountViewSet,
    DiscountUsageViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'inbox', ConversationInboxView, basename='inbox')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'participants', ParticipantViewSet, basename='participant')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'discounts', DiscountViewSet, basename='discount')
router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')

urlpatterns = [
    path('api/chat/', include(router.urls)),
    path('api/chat/online-status/', OnlineStatusView.as_view({'post': 'create', 'get': 'list'}), name='online-status'),
    path('api/notifications/', include(router.urls)),
]
