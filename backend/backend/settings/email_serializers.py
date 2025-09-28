from rest_framework import serializers
from django.contrib.auth import get_user_model
from .email_model import EmailSettings, EmailTemplate, EmailLog
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class EmailSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for EmailSettings model
    """
    # Read-only fields
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    last_tested_formatted = serializers.DateTimeField(source='last_tested', read_only=True)
    test_status_display = serializers.CharField(source='get_test_status_display', read_only=True)
    
    # Computed fields
    is_currently_active = serializers.SerializerMethodField()
    can_be_deleted = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailSettings
        fields = [
            'id', 'name', 'email_address', 'email_password', 'smtp_host', 'smtp_port',
            'smtp_username', 'smtp_password', 'use_tls', 'use_ssl', 'security_type',
            'from_name', 'from_email', 'reply_to_email', 'email_provider', 'provider_settings',
            'is_active', 'is_primary', 'priority', 'use_for_registration', 'use_for_password_reset',
            'use_for_order_notifications', 'use_for_admin_notifications', 'use_for_support',
            'last_tested', 'test_status', 'test_message', 'created_by_username',
            'last_tested_formatted', 'test_status_display', 'is_currently_active', 'can_be_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'last_tested', 'test_status', 'test_message']
    
    def get_is_currently_active(self, obj):
        """Check if this is the currently active email configuration"""
        return obj.is_active and obj.is_primary
    
    def get_can_be_deleted(self, obj):
        """Check if this email configuration can be deleted"""
        # Can't delete if it's the only active email or if it's primary
        if obj.is_primary:
            return False
        if obj.is_active and EmailSettings.objects.filter(created_by=obj.created_by, is_active=True).count() <= 1:
            return False
        return True
    
    def validate_email_address(self, value):
        """Validate email address format"""
        validator = EmailValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
    
    def validate_smtp_port(self, value):
        """Validate SMTP port"""
        if not (1 <= value <= 65535):
            raise serializers.ValidationError("Port must be between 1 and 65535.")
        return value
    
    def validate_priority(self, value):
        """Validate priority value"""
        if value < 1:
            raise serializers.ValidationError("Priority must be at least 1.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Validate TLS/SSL settings
        if data.get('use_tls') and data.get('use_ssl'):
            raise serializers.ValidationError("Cannot use both TLS and SSL simultaneously.")
        
        # Validate security type
        security_type = data.get('security_type', 'tls')
        if security_type == 'tls' and not data.get('use_tls'):
            data['use_tls'] = True
        elif security_type == 'ssl' and not data.get('use_ssl'):
            data['use_ssl'] = True
        elif security_type == 'none':
            data['use_tls'] = False
            data['use_ssl'] = False
        
        # Validate email addresses
        if 'from_email' in data:
            validator = EmailValidator()
            try:
                validator(data['from_email'])
            except ValidationError:
                raise serializers.ValidationError({"from_email": "Enter a valid from email address."})
        
        if 'reply_to_email' in data and data['reply_to_email']:
            validator = EmailValidator()
            try:
                validator(data['reply_to_email'])
            except ValidationError:
                raise serializers.ValidationError({"reply_to_email": "Enter a valid reply-to email address."})
        
        return data
    
    def create(self, validated_data):
        """Create new email settings"""
        # Set created_by from request user
        validated_data['created_by'] = self.context['request'].user
        
        # If this is the first email setting, make it primary and active
        user = validated_data['created_by']
        existing_count = EmailSettings.objects.filter(created_by=user).count()
        if existing_count == 0:
            validated_data['is_primary'] = True
            validated_data['is_active'] = True
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update email settings"""
        # Handle primary email logic
        if validated_data.get('is_primary', False):
            # Unset other primary emails for this user
            EmailSettings.objects.filter(
                created_by=instance.created_by,
                is_primary=True
            ).exclude(pk=instance.pk).update(is_primary=False)
        
        return super().update(instance, validated_data)


class EmailSettingsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for email settings list view
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    test_status_display = serializers.CharField(source='get_test_status_display', read_only=True)
    
    class Meta:
        model = EmailSettings
        fields = [
            'id', 'name', 'email_address', 'email_provider', 'smtp_host', 'smtp_port',
            'smtp_username', 'use_tls', 'use_ssl', 'from_name', 'from_email', 'reply_to_email',
            'is_active', 'is_primary', 'priority', 'test_status', 'test_status_display', 
            'created_by_username', 'last_tested', 'created_at'
        ]


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for EmailTemplate model
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    # Computed fields
    variable_count = serializers.SerializerMethodField()
    preview_content = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display', 'subject',
            'html_content', 'text_content', 'available_variables', 'sample_data',
            'is_active', 'is_default', 'created_by_username', 'variable_count',
            'preview_content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_variable_count(self, obj):
        """Get count of available variables"""
        return len(obj.available_variables) if obj.available_variables else 0
    
    def get_preview_content(self, obj):
        """Get preview of rendered content with sample data"""
        if obj.sample_data:
            try:
                rendered = obj.get_rendered_content(obj.sample_data)
                return {
                    'subject': rendered['subject'][:100] + '...' if len(rendered['subject']) > 100 else rendered['subject'],
                    'html_preview': rendered['html'][:200] + '...' if len(rendered['html']) > 200 else rendered['html'],
                    'text_preview': rendered['text'][:200] + '...' if len(rendered['text']) > 200 else rendered['text']
                }
            except Exception:
                return None
        return None
    
    def validate_name(self, value):
        """Validate template name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Template name cannot be empty.")
        return value.strip()
    
    def validate_subject(self, value):
        """Validate email subject"""
        if not value or not value.strip():
            raise serializers.ValidationError("Email subject cannot be empty.")
        return value.strip()
    
    def validate_html_content(self, value):
        """Validate HTML content"""
        if not value or not value.strip():
            raise serializers.ValidationError("HTML content cannot be empty.")
        return value.strip()
    
    def validate_available_variables(self, value):
        """Validate available variables format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Available variables must be a list.")
        
        for var in value:
            if not isinstance(var, str) or not var.strip():
                raise serializers.ValidationError("Each variable must be a non-empty string.")
        
        return value
    
    def create(self, validated_data):
        """Create new email template"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EmailTemplateListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for email template list view
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    variable_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display', 'subject',
            'is_active', 'is_default', 'created_by_username', 'variable_count',
            'created_at', 'updated_at'
        ]
    
    def get_variable_count(self, obj):
        """Get count of available variables"""
        return len(obj.available_variables) if obj.available_variables else 0


class EmailLogSerializer(serializers.ModelSerializer):
    """
    Serializer for EmailLog model
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    template_name = serializers.CharField(source='template_used.name', read_only=True)
    email_settings_name = serializers.CharField(source='email_settings_used.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'to_email', 'from_email', 'subject', 'status', 'status_display',
            'status_message', 'template_name', 'email_settings_name', 'user_username',
            'sent_at', 'delivered_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SMTPTestSerializer(serializers.Serializer):
    """
    Serializer for SMTP connection testing
    """
    smtp_host = serializers.CharField(max_length=255)
    smtp_port = serializers.IntegerField(min_value=1, max_value=65535)
    smtp_username = serializers.CharField(max_length=255)
    smtp_password = serializers.CharField(max_length=500)
    use_tls = serializers.BooleanField(default=True)
    use_ssl = serializers.BooleanField(default=False)
    test_email = serializers.EmailField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate SMTP test data"""
        if data.get('use_tls') and data.get('use_ssl'):
            raise serializers.ValidationError("Cannot use both TLS and SSL simultaneously.")
        
        return data


class EmailSendSerializer(serializers.Serializer):
    """
    Serializer for sending test emails
    """
    to_email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    html_content = serializers.CharField(required=False)
    text_content = serializers.CharField(required=False)
    template_id = serializers.IntegerField(required=False)
    template_variables = serializers.JSONField(required=False, default=dict)
    email_settings_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """Validate email send data"""
        if not data.get('html_content') and not data.get('text_content') and not data.get('template_id'):
            raise serializers.ValidationError("Either content or template must be provided.")
        
        return data


class EmailSettingsBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk updating email settings
    """
    email_settings_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('set_primary', 'Set as Primary'),
        ('delete', 'Delete'),
    ])
    
    def validate_email_settings_ids(self, value):
        """Validate email settings IDs"""
        user = self.context['request'].user
        valid_ids = EmailSettings.objects.filter(
            created_by=user,
            id__in=value
        ).values_list('id', flat=True)
        
        if len(valid_ids) != len(value):
            invalid_ids = set(value) - set(valid_ids)
            raise serializers.ValidationError(f"Invalid email settings IDs: {list(invalid_ids)}")
        
        return value


class EmailTemplatePreviewSerializer(serializers.Serializer):
    """
    Serializer for email template preview
    """
    template_id = serializers.IntegerField()
    preview_data = serializers.JSONField(default=dict)
    
    def validate_template_id(self, value):
        """Validate template ID"""
        user = self.context['request'].user
        if not EmailTemplate.objects.filter(id=value, created_by=user).exists():
            raise serializers.ValidationError("Template not found or access denied.")
        return value
