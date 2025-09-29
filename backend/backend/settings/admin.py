from django.contrib import admin
from .email_model import EmailSettings, EmailTemplate, EmailLog
from .footer_settings_model import FooterSettings, SocialMediaLink

# Register your models here.

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'email_address', 'email_provider', 'is_active', 'is_primary', 'created_by', 'created_at']
    list_filter = ['email_provider', 'is_active', 'is_primary', 'created_at']
    search_fields = ['name', 'email_address', 'smtp_host']
    readonly_fields = ['created_at', 'updated_at', 'last_tested']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email_address', 'email_password')
        }),
        ('SMTP Configuration', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_password')
        }),
        ('Security Settings', {
            'fields': ('use_tls', 'use_ssl', 'security_type')
        }),
        ('Email Settings', {
            'fields': ('from_name', 'from_email', 'reply_to_email')
        }),
        ('Status & Priority', {
            'fields': ('is_active', 'is_primary', 'priority')
        }),
        ('Usage Settings', {
            'fields': ('use_for_registration', 'use_for_password_reset', 'use_for_order_notifications', 'use_for_admin_notifications', 'use_for_support')
        }),
        ('Test Results', {
            'fields': ('test_status', 'test_message', 'last_tested'),
            'classes': ('collapse',)
        })
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'subject', 'is_active', 'is_default', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'subject', 'template_type']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['to_email', 'from_email', 'subject', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['to_email', 'from_email', 'subject']
    readonly_fields = ['created_at', 'sent_at', 'delivered_at']


class SocialMediaLinkInline(admin.TabularInline):
    model = SocialMediaLink
    extra = 1
    fields = ['platform', 'url', 'icon', 'is_active', 'order']


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'phone', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SocialMediaLinkInline]
    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Content', {
            'fields': ('description', 'about_us', 'copyright', 'mission', 'vision')
        }),
        ('Business Information', {
            'fields': ('business_hours', 'quick_response')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'footer_setting', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'platform', 'created_at']
    search_fields = ['platform', 'url', 'footer_setting__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['footer_setting', 'order', 'platform']
