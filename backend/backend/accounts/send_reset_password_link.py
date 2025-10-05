import secrets
import hashlib
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from accounts.models import User
from django.conf import settings

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def create_reset_link(token):
    """Create the password reset link"""
    frontend_url = getattr(settings, 'FRONTEND_BASE_URL')
    return f"{frontend_url}/reset-password?token={token}"

def send_password_reset_email(user_email):
    """
    Send password reset email to user
    Returns: (success: bool, message: str)
    """
    try:
        # Check if user exists
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return False, "No account found with this email address"
        
        # Generate reset token
        reset_token = generate_reset_token()
        
        # Set token and expiry time (24 hours from now)
        user.password_reset_token = reset_token
        user.password_reset_token_expires = timezone.now() + timedelta(hours=24)
        user.save()
        
        # Create reset link
        reset_link = create_reset_link(reset_token)
        
        # Get primary email settings
        from accounts.email_verification_service import EmailVerificationService
        email_settings = EmailVerificationService.get_primary_email_settings()
        
        if not email_settings:
            return False, "Email service not configured"
        
        # Email subject and content
        subject = "Password Reset Request - GreatKart"
        
        # Use template from email_templates folder
        from django.template.loader import render_to_string
        from settings.models import Logo
        from settings.footer_settings_model import FooterSettings
        
        # Get company info
        logo = Logo.objects.filter(is_active=True).first()
        footer = FooterSettings.objects.filter(is_active=True).first()
        
        context = {
            'customer_name': user.profile.full_name or user.email,
            'reset_link': reset_link,
            'company_name': 'GreatKart',
            'company_email': footer.email if footer else 'info@greatkart.com',
            'company_phone': footer.phone if footer else '+880-123-456-789',
            'company_address': 'Dhaka, Bangladesh',
            'logo_url': logo.logo_url if logo else None
        }
        
        # Render template
        html_message = render_to_string('authentication/password_reset.html', context)
        
        # Plain text version
        text_message = f"""
        Password Reset Request - GreatKart
        
        Hello {user.profile.full_name or user.email},
        
        We received a request to reset your password for your GreatKart account.
        
        To reset your password, click the link below:
        {reset_link}
        
        Important: This link will expire in 24 hours for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        GreatKart Team
        """
        
        # Send email using SMTP
        from accounts.email_verification_service import EmailVerificationService
        
        success = EmailVerificationService._send_smtp_email(
            email_settings=email_settings,
            to_email=user_email,
            subject=subject,
            html_content=html_message,
            text_content=text_message
        )
        
        if success:
            return True, "Password reset instructions have been sent to your email address"
        else:
            return False, "Failed to send email. Please try again later"
            
    except Exception as e:

        return False, "An error occurred while sending the email"

def verify_reset_token(token):
    """
    Verify if reset token is valid and not expired
    Returns: (is_valid: bool, user: User or None, message: str)
    """
    try:
        user = User.objects.get(password_reset_token=token)
        
        # Check if token is expired
        if user.password_reset_token_expires and user.password_reset_token_expires < timezone.now():
            return False, None, "Reset link has expired. Please request a new one."
        
        return True, user, "Token is valid"
        
    except User.DoesNotExist:
        return False, None, "Invalid reset link. Please request a new one."
    except Exception as e:

        return False, None, "An error occurred while verifying the reset link"

def clear_reset_token(user):
    """Clear the reset token after successful password reset"""
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.save()
