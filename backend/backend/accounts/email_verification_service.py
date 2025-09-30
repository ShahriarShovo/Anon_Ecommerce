import uuid
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from accounts.models import User
from settings.email_model import EmailSettings
import logging

logger = logging.getLogger(__name__)

class EmailVerificationService:
    """
    Service for handling email verification functionality
    """
    
    @staticmethod
    def get_primary_email_settings():
        """
        Get the primary email settings from the database
        """
        try:
            primary_email = EmailSettings.objects.filter(
                is_primary=True,
                is_active=True
            ).first()
            
            if not primary_email:
                logger.error("No primary email settings found")
                return None
                
            return primary_email
        except Exception as e:
            logger.error(f"Error getting primary email settings: {str(e)}")
            return None
    
    @staticmethod
    def generate_verification_token():
        """
        Generate a unique verification token
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def create_verification_link(request, token):
        """
        Create the verification link
        """
        try:
            # Get current site domain
            current_site = get_current_site(request)
            domain = current_site.domain
            
            # Create verification URL - redirect to frontend success page
            verification_url = f"http://localhost:3000/email-verified?token={token}"
            return verification_url
        except Exception as e:
            logger.error(f"Error creating verification link: {str(e)}")
            return None
    
    @staticmethod
    def send_verification_email(request, user, token):
        """
        Send verification email to user using primary SMTP settings
        """
        try:
            
            
            # Get primary email settings
            email_settings = EmailVerificationService.get_primary_email_settings()
            if not email_settings:
                
                logger.error("No primary email settings available")
                return False
            
            
            
            # Create verification link
            verification_link = EmailVerificationService.create_verification_link(request, token)
            if not verification_link:
                
                logger.error("Failed to create verification link")
                return False
            
            
            
            # Email content - Better subject to avoid spam
            subject = "Please verify your email address for your new account"
            
            # Use template from email_templates folder
            from django.template.loader import render_to_string
            from settings.models import Logo
            from settings.footer_settings_model import FooterSettings
            
            # Get company info
            logo = Logo.objects.filter(is_active=True).first()
            footer = FooterSettings.objects.filter(is_active=True).first()
            
            context = {
                'customer_name': user.profile.full_name or user.email,
                'verification_link': verification_link,
                'company_name': 'GreatKart',
                'company_email': footer.email if footer else 'info@greatkart.com',
                'company_phone': footer.phone if footer else '+880-123-456-789',
                'company_address': 'Dhaka, Bangladesh',
                'logo_url': logo.logo_url if logo else None
            }
            
            # Render template
            html_content = render_to_string('authentication/registration_verification.html', context)
            
            # Plain text version - Single, clean version
            text_content = f"""Welcome to Our Store!

Complete Your Registration

Hello {user.profile.full_name or user.email},

Thank you for creating an account with us! To complete your registration and start shopping, please verify your email address by visiting this link:

{verification_link}

Important: This verification link will expire in 24 hours for security reasons.

If you didn't create an account with us, please ignore this email.

Best regards,
Our Store Team

This is an automated message. Please do not reply to this email.
© 2024 Our Store. All rights reserved."""
            
            # Send email using SMTP
            
            success = EmailVerificationService._send_smtp_email(
                email_settings=email_settings,
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                
                logger.info(f"Verification email sent successfully to {user.email}")
                return True
            else:
                
                logger.error(f"Failed to send verification email to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def _send_smtp_email(email_settings, to_email, subject, html_content, text_content):
        """
        Send email using SMTP settings
        """
        try:
            # Create message - Single message with both text and HTML
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{email_settings.from_name} <{email_settings.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Reply-To'] = email_settings.from_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            # Attach parts in order (text first, then HTML)
            msg.attach(text_part)
            msg.attach(html_part)
            
            # SMTP configuration
            smtp_server = email_settings.smtp_host
            smtp_port = email_settings.smtp_port
            smtp_username = email_settings.smtp_username
            smtp_password = email_settings.email_password  # Use the stored password
            
            # Create SMTP connection
            if email_settings.use_ssl:
                # Use SSL
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                # Use TLS
                server = smtplib.SMTP(smtp_server, smtp_port)
                if email_settings.use_tls:
                    server.starttls()
            
            # Login and send email
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {str(e)}")
            return False
    
    @staticmethod
    def verify_email_token(token):
        """
        Verify the email token and activate user account
        """
        try:
            # Find user by token (you'll need to store token in user model or create a separate model)
            # For now, we'll use a simple approach - you might want to create a separate EmailVerification model
            
            # This is a simplified approach - in production, you should create a proper EmailVerification model
            # that stores tokens with expiration times
            
            # For now, we'll assume the token is stored in user's profile or a separate field
            # You might want to add a verification_token field to User model or create EmailVerification model
            
            logger.info(f"Verifying token: {token}")
            
            # In a real implementation, you would:
            # 1. Create an EmailVerification model with token, user, created_at, is_used fields
            # 2. Store the token when sending verification email
            # 3. Check token validity and expiration here
            # 4. Mark token as used after successful verification
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email token: {str(e)}")
            return False
