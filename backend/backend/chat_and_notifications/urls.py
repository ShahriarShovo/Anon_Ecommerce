from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet,
    ConversationInboxView,
    MessageViewSet,
    MessageMarkReadView,
    ParticipantViewSet,
    OnlineStatusView,
    # NotificationViewSet,
    # NotificationPublicView,
    # DiscountViewSet,
    # DiscountUsageViewSet
)
from .views.contact.contact import (
    ContactListCreateView,
    ContactDetailView,
    contact_stats,
    mark_as_read,
    mark_as_replied
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'inbox', ConversationInboxView, basename='inbox')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'participants', ParticipantViewSet, basename='participant')
# router.register(r'notifications', NotificationViewSet, basename='notification')
# router.register(r'discounts', DiscountViewSet, basename='discount')
# router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')

urlpatterns = [
    path('api/chat/', include(router.urls)),
    path('api/chat/online-status/', OnlineStatusView.as_view({'post': 'create', 'get': 'list'}), name='online-status'),
    # path('api/notifications/', include(router.urls)),
    
    # Contact API endpoints
    path('api/chat_and_notifications/contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('api/chat_and_notifications/contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('api/chat_and_notifications/contacts/stats/', contact_stats, name='contact-stats'),
    path('api/chat_and_notifications/contacts/<int:contact_id>/mark-read/', mark_as_read, name='contact-mark-read'),
    path('api/chat_and_notifications/contacts/<int:contact_id>/mark-replied/', mark_as_replied, name='contact-mark-replied'),
]
