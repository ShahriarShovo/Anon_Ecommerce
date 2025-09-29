import secrets
import hashlib
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from accounts.models import User


def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def create_reset_link(token):
    """Create the password reset link"""
    return f"http://localhost:3000/reset-password?token={token}"


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
        
        # HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #007bff; margin-bottom: 20px;">
                    <i class="fa fa-lock" style="margin-right: 10px;"></i>
                    Password Reset Request
                </h2>
                
                <p style="font-size: 16px; margin-bottom: 25px;">
                    Hello <strong>{user.profile.full_name or user.email}</strong>,
                </p>
                
                <p style="font-size: 16px; margin-bottom: 25px;">
                    We received a request to reset your password for your GreatKart account.
                </p>
                
                <div style="background: #fff; padding: 25px; border-radius: 8px; border: 1px solid #dee2e6; margin: 25px 0;">
                    <p style="margin-bottom: 20px; font-size: 16px;">
                        Click the button below to reset your password:
                    </p>
                    
                    <a href="{reset_link}" 
                       style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                        Reset My Password
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #6c757d; margin-top: 25px;">
                    If the button doesn't work, copy and paste this link into your browser:
                </p>
                <p style="font-size: 12px; color: #6c757d; word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {reset_link}
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="font-size: 14px; color: #6c757d; margin: 0;">
                        <strong>Important:</strong> This link will expire in 24 hours for security reasons.
                    </p>
                    <p style="font-size: 14px; color: #6c757d; margin: 10px 0 0 0;">
                        If you didn't request this password reset, please ignore this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
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
        print(f"Error sending password reset email: {str(e)}")
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
        print(f"Error verifying reset token: {str(e)}")
        return False, None, "An error occurred while verifying the reset link"


def clear_reset_token(user):
    """Clear the reset token after successful password reset"""
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.save()
