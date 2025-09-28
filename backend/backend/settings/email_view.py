from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from .email_model import EmailSettings, EmailTemplate, EmailLog
from .email_serializers import (
    EmailSettingsSerializer, EmailSettingsListSerializer,
    EmailTemplateSerializer, EmailTemplateListSerializer,
    EmailLogSerializer, SMTPTestSerializer, EmailSendSerializer,
    EmailSettingsBulkUpdateSerializer, EmailTemplatePreviewSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailSettingsListCreateView(generics.ListCreateAPIView):
    """
    List and create email settings
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmailSettingsListSerializer
        return EmailSettingsSerializer
    
    def get_queryset(self):
        return EmailSettings.objects.filter(created_by=self.request.user).order_by('priority', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailSettingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete email settings
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSettingsSerializer
    
    def get_queryset(self):
        return EmailSettings.objects.filter(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Check if this is the only active email
        if instance.is_active and EmailSettings.objects.filter(
            created_by=self.request.user, 
            is_active=True
        ).count() <= 1:
            raise ValueError("Cannot delete the only active email configuration.")
        
        # Allow deletion of primary email configuration
        # Admin can delete any email configuration including primary ones
        
        instance.delete()


class EmailTemplateListCreateView(generics.ListCreateAPIView):
    """
    List and create email templates
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmailTemplateListSerializer
        return EmailTemplateSerializer
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(created_by=self.request.user).order_by('template_type', 'name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete email templates
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailTemplateSerializer
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(created_by=self.request.user)


class EmailLogListView(generics.ListAPIView):
    """
    List email logs
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailLogSerializer
    
    def get_queryset(self):
        return EmailLog.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:100]  # Limit to last 100 logs


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_smtp_connection(request):
    """
    Test SMTP connection with provided credentials
    """
    print(f"SMTP Test Request Data: {request.data}")  # Debug print
    serializer = SMTPTestSerializer(data=request.data)
    if not serializer.is_valid():
        print(f"SMTP Test Validation Errors: {serializer.errors}")  # Debug print
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Create SMTP connection
        if data['use_ssl']:
            server = smtplib.SMTP_SSL(data['smtp_host'], data['smtp_port'])
        else:
            server = smtplib.SMTP(data['smtp_host'], data['smtp_port'])
            if data['use_tls']:
                server.starttls()
        
        # Authenticate
        server.login(data['smtp_username'], data['smtp_password'])
        
        # Test email sending if test_email provided
        if data.get('test_email'):
            msg = MIMEMultipart()
            msg['From'] = data['smtp_username']
            msg['To'] = data['test_email']
            msg['Subject'] = "SMTP Test Email"
            
            body = "This is a test email to verify SMTP configuration."
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
        
        server.quit()
        
        return Response({
            'success': True,
            'message': 'SMTP connection successful!'
        }, status=status.HTTP_200_OK)
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        print(f"SMTP Authentication Error: {str(e)}")  # Debug print
        return Response({
            'success': False,
            'message': f'Authentication failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP Connection Error: {str(e)}")
        print(f"SMTP Connection Error: {str(e)}")  # Debug print
        return Response({
            'success': False,
            'message': f'Connection failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'SMTP error: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        print(f"Unexpected SMTP Error: {str(e)}")  # Debug print
        return Response({
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_email_settings(request, pk):
    """
    Test specific email settings configuration
    """
    try:
        email_settings = EmailSettings.objects.get(
            id=pk, 
            created_by=request.user
        )
    except EmailSettings.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Email settings not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Get SMTP configuration
        smtp_config = email_settings.get_smtp_config()
        
        # Create SMTP connection
        if smtp_config['use_ssl']:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            if smtp_config['use_tls']:
                server.starttls()
        
        # Authenticate
        server.login(smtp_config['username'], smtp_config['password'])
        
        # Test email sending
        test_email = request.data.get('test_email', smtp_config['from_email'])
        if test_email:
            msg = MIMEMultipart()
            msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
            msg['To'] = test_email
            msg['Subject'] = "Email Settings Test"
            
            body = f"""
            This is a test email from your email settings configuration.
            
            Settings Name: {email_settings.name}
            SMTP Host: {smtp_config['host']}
            SMTP Port: {smtp_config['port']}
            Security: {'SSL' if smtp_config['use_ssl'] else 'TLS' if smtp_config['use_tls'] else 'None'}
            
            If you receive this email, your SMTP configuration is working correctly!
            """
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
        
        server.quit()
        
        # Update test status
        email_settings.update_test_status(True, "Connection test successful")
        
        return Response({
            'success': True,
            'message': 'Email settings test successful!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Email Settings Test Error: {str(e)}")
        
        # Update test status
        email_settings.update_test_status(False, str(e))
        
        return Response({
            'success': False,
            'message': f'Test failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_email(request):
    """
    Send test email using specified email settings
    """
    serializer = EmailSendSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Get email settings
        if data.get('email_settings_id'):
            email_settings = EmailSettings.objects.get(
                id=data['email_settings_id'],
                created_by=request.user
            )
        else:
            # Get primary active email settings
            email_settings = EmailSettings.objects.filter(
                created_by=request.user,
                is_active=True,
                is_primary=True
            ).first()
            
            if not email_settings:
                return Response({
                    'success': False,
                    'message': 'No active email settings found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get template if specified
        template = None
        if data.get('template_id'):
            template = EmailTemplate.objects.get(
                id=data['template_id'],
                created_by=request.user
            )
        
        # Prepare email content
        if template:
            rendered = template.get_rendered_content(data.get('template_variables', {}))
            subject = rendered['subject']
            html_content = rendered['html']
            text_content = rendered['text']
        else:
            subject = data['subject']
            html_content = data.get('html_content', '')
            text_content = data.get('text_content', '')
        
        # Send email
        smtp_config = email_settings.get_smtp_config()
        
        if smtp_config['use_ssl']:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            if smtp_config['use_tls']:
                server.starttls()
        
        server.login(smtp_config['username'], smtp_config['password'])
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg['To'] = data['to_email']
        msg['Subject'] = subject
        
        if smtp_config.get('reply_to'):
            msg['Reply-To'] = smtp_config['reply_to']
        
        # Add content
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        # Log email
        EmailLog.objects.create(
            to_email=data['to_email'],
            from_email=smtp_config['from_email'],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            status='sent',
            template_used=template,
            email_settings_used=email_settings,
            user=request.user,
            sent_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': 'Test email sent successfully!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Send Test Email Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_email_settings(request):
    """
    Bulk update email settings (activate, deactivate, set primary, delete)
    """
    serializer = EmailSettingsBulkUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    email_settings_ids = data['email_settings_ids']
    action = data['action']
    
    try:
        with transaction.atomic():
            email_settings = EmailSettings.objects.filter(
                id__in=email_settings_ids,
                created_by=request.user
            )
            
            if action == 'activate':
                email_settings.update(is_active=True)
                message = f"Activated {len(email_settings_ids)} email settings"
                
            elif action == 'deactivate':
                email_settings.update(is_active=False)
                message = f"Deactivated {len(email_settings_ids)} email settings"
                
            elif action == 'set_primary':
                # First, unset all primary emails for this user
                EmailSettings.objects.filter(created_by=request.user).update(is_primary=False)
                # Then set the selected ones as primary
                email_settings.update(is_primary=True, is_active=True)
                message = f"Set {len(email_settings_ids)} email settings as primary"
                
            elif action == 'delete':
                # Check if trying to delete primary email
                primary_emails = email_settings.filter(is_primary=True)
                if primary_emails.exists():
                    return Response({
                        'success': False,
                        'message': 'Cannot delete primary email settings'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                count = email_settings.count()
                email_settings.delete()
                message = f"Deleted {count} email settings"
            
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Bulk Update Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Bulk update failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_email_template(request):
    """
    Preview email template with sample data
    """
    serializer = EmailTemplatePreviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    template_id = data['template_id']
    preview_data = data['preview_data']
    
    try:
        template = EmailTemplate.objects.get(
            id=template_id,
            created_by=request.user
        )
        
        rendered = template.get_rendered_content(preview_data)
        
        return Response({
            'success': True,
            'preview': rendered
        }, status=status.HTTP_200_OK)
        
    except EmailTemplate.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Template not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Template Preview Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Preview failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_email_settings(request):
    """
    Get currently active email settings for the user
    """
    try:
        # Get primary active email settings
        email_settings = EmailSettings.objects.filter(
            created_by=request.user,
            is_active=True,
            is_primary=True
        ).first()
        
        if not email_settings:
            return Response({
                'success': False,
                'message': 'No active email settings found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmailSettingsSerializer(email_settings)
        
        return Response({
            'success': True,
            'email_settings': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get Active Email Settings Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to get active email settings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_statistics(request):
    """
    Get email statistics for the user
    """
    try:
        user = request.user
        
        # Email settings statistics
        total_settings = EmailSettings.objects.filter(created_by=user).count()
        active_settings = EmailSettings.objects.filter(created_by=user, is_active=True).count()
        primary_settings = EmailSettings.objects.filter(created_by=user, is_primary=True).count()
        
        # Email logs statistics
        total_emails = EmailLog.objects.filter(user=user).count()
        sent_emails = EmailLog.objects.filter(user=user, status='sent').count()
        failed_emails = EmailLog.objects.filter(user=user, status='failed').count()
        
        # Template statistics
        total_templates = EmailTemplate.objects.filter(created_by=user).count()
        active_templates = EmailTemplate.objects.filter(created_by=user, is_active=True).count()
        
        return Response({
            'success': True,
            'statistics': {
                'email_settings': {
                    'total': total_settings,
                    'active': active_settings,
                    'primary': primary_settings
                },
                'email_logs': {
                    'total': total_emails,
                    'sent': sent_emails,
                    'failed': failed_emails
                },
                'templates': {
                    'total': total_templates,
                    'active': active_templates
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get Email Statistics Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to get email statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
