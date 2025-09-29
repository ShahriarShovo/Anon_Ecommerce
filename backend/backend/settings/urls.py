from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogoViewSet, BannerViewSet
from .email_view import (
    EmailSettingsListCreateView, EmailSettingsDetailView,
    EmailTemplateListCreateView, EmailTemplateDetailView,
    EmailLogListView, test_smtp_connection, test_email_settings,
    send_test_email, bulk_update_email_settings, preview_email_template,
    get_active_email_settings, get_email_statistics
)
from .footer_settings_views import (
    FooterSettingsListCreateView, FooterSettingsDetailView,
    SocialMediaLinkListCreateView, SocialMediaLinkDetailView,
    get_active_footer_settings, bulk_update_social_links
)

router = DefaultRouter()
router.register(r'logos', LogoViewSet)
router.register(r'banners', BannerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Email Settings URLs
    path('email-settings/', EmailSettingsListCreateView.as_view(), name='email-settings-list'),
    path('email-settings/<int:pk>/', EmailSettingsDetailView.as_view(), name='email-settings-detail'),
    path('email-settings/<int:pk>/test/', test_email_settings, name='test-email-settings'),
    path('email-settings/bulk-update/', bulk_update_email_settings, name='bulk-update-email-settings'),
    path('email-settings/active/', get_active_email_settings, name='get-active-email-settings'),
    
    # Email Templates URLs
    path('email-templates/', EmailTemplateListCreateView.as_view(), name='email-templates-list'),
    path('email-templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-templates-detail'),
    path('email-templates/preview/', preview_email_template, name='preview-email-template'),
    
    # Email Logs URLs
    path('email-logs/', EmailLogListView.as_view(), name='email-logs-list'),
    
    # SMTP Testing URLs
    path('smtp/test/', test_smtp_connection, name='test-smtp-connection'),
    path('email/send-test/', send_test_email, name='send-test-email'),
    
    # Statistics URLs
    path('email-statistics/', get_email_statistics, name='email-statistics'),
    
    # Footer Settings URLs
    path('footer-settings/', FooterSettingsListCreateView.as_view(), name='footer-settings-list'),
    path('footer-settings/<int:pk>/', FooterSettingsDetailView.as_view(), name='footer-settings-detail'),
    path('footer-settings/<int:footer_setting_id>/social-links/', SocialMediaLinkListCreateView.as_view(), name='social-links-list'),
    path('footer-settings/<int:footer_setting_id>/social-links/<int:pk>/', SocialMediaLinkDetailView.as_view(), name='social-links-detail'),
    path('footer-settings/<int:footer_setting_id>/social-links/bulk-update/', bulk_update_social_links, name='bulk-update-social-links'),
    path('footer-settings/active/', get_active_footer_settings, name='get-active-footer-settings'),
]
