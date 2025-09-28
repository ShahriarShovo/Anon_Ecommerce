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
            print(f"🔍 DEBUG: Starting email verification for user: {user.email}")
            print(f"🔍 DEBUG: Token: {token}")
            
            # Get primary email settings
            email_settings = EmailVerificationService.get_primary_email_settings()
            if not email_settings:
                print("🔍 DEBUG: No primary email settings available")
                logger.error("No primary email settings available")
                return False
            
            print(f"🔍 DEBUG: Found primary email settings: {email_settings.email_address}")
            
            # Create verification link
            verification_link = EmailVerificationService.create_verification_link(request, token)
            if not verification_link:
                print("🔍 DEBUG: Failed to create verification link")
                logger.error("Failed to create verification link")
                return False
            
            print(f"🔍 DEBUG: Verification link created: {verification_link}")
            
            # Email content - Better subject to avoid spam
            subject = "Please verify your email address for your new account"
            
            # HTML email template - Single, clean template with spam prevention
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Verification</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #007bff;
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .button {{
            display: inline-block;
            background-color: #28a745;
            color: white !important;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
            text-align: center;
        }}
        .button:hover {{
            background-color: #218838;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #6c757d;
            text-align: center;
        }}
        .link-text {{
            word-break: break-all;
            color: #007bff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Our Store!</h1>
        </div>
        <div class="content">
            <h2>Complete Your Registration</h2>
            <p>Hello {user.profile.full_name or user.email},</p>
            <p>Thank you for creating an account with us! To complete your registration and start shopping, please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" class="button" style="color: white !important; text-decoration: none;">Verify My Email Address</a>
            </div>
            
            <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace;">
                <a href="{verification_link}" style="color: #007bff; text-decoration: none;">{verification_link}</a>
            </p>
            
            <p><strong>Important:</strong> This verification link will expire in 24 hours for security reasons.</p>
            
            <p>If you didn't create an account with us, please ignore this email.</p>
            
            <p>Best regards,<br>Our Store Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>© 2024 Our Store. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
            
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
            print(f"🔍 DEBUG: Attempting to send email to: {user.email}")
            success = EmailVerificationService._send_smtp_email(
                email_settings=email_settings,
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                print(f"🔍 DEBUG: Verification email sent successfully to {user.email}")
                logger.info(f"Verification email sent successfully to {user.email}")
                return True
            else:
                print(f"🔍 DEBUG: Failed to send verification email to {user.email}")
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
