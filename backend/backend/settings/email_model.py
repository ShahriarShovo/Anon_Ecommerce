from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
import json

User = get_user_model()

class EmailSettings(models.Model):
    """
    Model to store email configuration settings
    """
    EMAIL_PROVIDER_CHOICES = [
        ('smtp', 'SMTP'),
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('yahoo', 'Yahoo'),
        ('custom', 'Custom SMTP'),
    ]
    
    SECURITY_CHOICES = [
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
        ('none', 'None'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, help_text="Friendly name for this email configuration")
    email_address = models.EmailField(validators=[EmailValidator()], help_text="Email address to send from")
    email_password = models.CharField(max_length=500, help_text="Email password (encrypted)")
    
    # SMTP Configuration
    smtp_host = models.CharField(max_length=255, help_text="SMTP server host")
    smtp_port = models.PositiveIntegerField(default=587, help_text="SMTP server port")
    smtp_username = models.CharField(max_length=255, blank=True, null=True, help_text="SMTP username (if different from email)")
    smtp_password = models.CharField(max_length=500, blank=True, null=True, help_text="SMTP password (if different from email password)")
    
    # Security Settings
    use_tls = models.BooleanField(default=True, help_text="Use TLS encryption")
    use_ssl = models.BooleanField(default=False, help_text="Use SSL encryption")
    security_type = models.CharField(max_length=10, choices=SECURITY_CHOICES, default='tls')
    
    # Email Settings
    from_name = models.CharField(max_length=100, help_text="Display name for sender")
    from_email = models.EmailField(help_text="From email address")
    reply_to_email = models.EmailField(blank=True, null=True, help_text="Reply-to email address")
    
    # Provider Settings
    email_provider = models.CharField(max_length=20, choices=EMAIL_PROVIDER_CHOICES, default='smtp')
    provider_settings = models.JSONField(default=dict, blank=True, help_text="Additional provider-specific settings")
    
    # Status and Priority
    is_active = models.BooleanField(default=True, help_text="Is this email configuration active?")
    is_primary = models.BooleanField(default=False, help_text="Is this the primary email configuration?")
    priority = models.PositiveIntegerField(default=1, help_text="Priority order (1 = highest)")
    
    # Usage Settings
    use_for_registration = models.BooleanField(default=True, help_text="Use for user registration emails")
    use_for_password_reset = models.BooleanField(default=True, help_text="Use for password reset emails")
    use_for_order_notifications = models.BooleanField(default=True, help_text="Use for order notifications")
    use_for_admin_notifications = models.BooleanField(default=True, help_text="Use for admin notifications")
    use_for_support = models.BooleanField(default=True, help_text="Use for support emails")
    
    # Testing and Status
    last_tested = models.DateTimeField(blank=True, null=True, help_text="Last time SMTP connection was tested")
    test_status = models.BooleanField(default=False, help_text="Last test result")
    test_message = models.TextField(blank=True, null=True, help_text="Last test result message")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_email_settings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Setting"
        verbose_name_plural = "Email Settings"
        ordering = ['priority', '-created_at']
        unique_together = ['email_address', 'created_by']
    
    def __str__(self):
        return f"{self.name} ({self.email_address})"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary email per user
        if self.is_primary:
            EmailSettings.objects.filter(
                created_by=self.created_by,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # Ensure only one active email per user if not multiple
        if self.is_active and not self.created_by.is_superuser:
            EmailSettings.objects.filter(
                created_by=self.created_by,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    def get_smtp_config(self):
        """Get SMTP configuration as dictionary"""
        return {
            'host': self.smtp_host,
            'port': self.smtp_port,
            'username': self.smtp_username or self.email_address,
            'password': self.smtp_password or self.email_password,
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl,
            'from_email': self.from_email,
            'from_name': self.from_name,
            'reply_to': self.reply_to_email,
        }
    
    def update_test_status(self, success, message):
        """Update test status and message"""
        from django.utils import timezone
        self.test_status = success
        self.test_message = message
        self.last_tested = timezone.now()
        self.save(update_fields=['test_status', 'test_message', 'last_tested'])

class EmailTemplate(models.Model):
    """
    Model to store email templates
    """
    TEMPLATE_TYPE_CHOICES = [
        ('registration', 'User Registration'),
        ('password_reset', 'Password Reset'),
        ('order_confirmation', 'Order Confirmation'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('admin_notification', 'Admin Notification'),
        ('support_reply', 'Support Reply'),
        ('welcome', 'Welcome Email'),
        ('newsletter', 'Newsletter'),
        ('custom', 'Custom Template'),
    ]
    
    # Template Information
    name = models.CharField(max_length=100, help_text="Template name")
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES, default='custom')
    subject = models.CharField(max_length=200, help_text="Email subject line")
    
    # Template Content
    html_content = models.TextField(help_text="HTML email template")
    text_content = models.TextField(blank=True, null=True, help_text="Plain text email template")
    
    # Template Variables
    available_variables = models.JSONField(default=list, blank=True, help_text="Available template variables")
    sample_data = models.JSONField(default=dict, blank=True, help_text="Sample data for preview")
    
    # Settings
    is_active = models.BooleanField(default=True, help_text="Is this template active?")
    is_default = models.BooleanField(default=False, help_text="Is this the default template for this type?")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_email_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        ordering = ['template_type', 'name']
        unique_together = ['template_type', 'created_by', 'is_default']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def save(self, *args, **kwargs):
        # Ensure only one default template per type per user
        if self.is_default:
            EmailTemplate.objects.filter(
                template_type=self.template_type,
                created_by=self.created_by,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def get_rendered_content(self, context=None):
        """Get rendered template content with context variables"""
        if not context:
            context = {}
        
        # Simple template variable replacement
        html_content = self.html_content
        text_content = self.text_content or ""
        
        for key, value in context.items():
            html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            text_content = text_content.replace(f"{{{{{key}}}}}", str(value))
        
        return {
            'html': html_content,
            'text': text_content,
            'subject': self.subject
        }

class EmailLog(models.Model):
    """
    Model to track email sending logs
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    # Email Information
    to_email = models.EmailField(help_text="Recipient email address")
    from_email = models.EmailField(help_text="Sender email address")
    subject = models.CharField(max_length=200, help_text="Email subject")
    
    # Content
    html_content = models.TextField(blank=True, null=True, help_text="HTML content sent")
    text_content = models.TextField(blank=True, null=True, help_text="Text content sent")
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_message = models.TextField(blank=True, null=True, help_text="Status message or error")
    
    # Template and Settings
    template_used = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, blank=True, null=True)
    email_settings_used = models.ForeignKey(EmailSettings, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Metadata
    sent_at = models.DateTimeField(blank=True, null=True, help_text="When email was sent")
    delivered_at = models.DateTimeField(blank=True, null=True, help_text="When email was delivered")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional Data
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='email_logs')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, blank=True, null=True)
    additional_data = models.JSONField(default=dict, blank=True, help_text="Additional tracking data")
    
    class Meta:
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_email', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.status})"
    
    def update_status(self, status, message=None):
        """Update email status"""
        from django.utils import timezone
        
        self.status = status
        if message:
            self.status_message = message
        
        if status == 'sent':
            self.sent_at = timezone.now()
        elif status == 'delivered':
            self.delivered_at = timezone.now()
        
        self.save(update_fields=['status', 'status_message', 'sent_at', 'delivered_at'])
