"""
Email Service for Sending Invoice Emails
========================================

This module handles sending invoice emails to customers when orders are created or delivered.
"""

import os
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from settings.email_model import EmailSettings
from settings.models import Logo
from settings.footer_settings_model import FooterSettings
from .invoice_generator import InvoiceGenerator
import logging

logger = logging.getLogger(__name__)


class InvoiceEmailService:
    """
    Service for sending invoice emails to customers
    """
    
    @staticmethod
    def get_email_settings():
        """Get primary email settings"""
        try:
            return EmailSettings.objects.filter(
                is_primary=True,
                is_active=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting email settings: {str(e)}")
            return None
    
    @staticmethod
    def get_company_info():
        """Get company information from settings"""
        try:
            # Get active logo
            logo = Logo.objects.filter(is_active=True).first()
            logo_url = logo.logo_url if logo else None
            
            # Get active footer settings
            footer = FooterSettings.objects.filter(is_active=True).first()
            
            return {
                'company_name': 'GreatKart',
                'company_email': footer.email if footer else 'info@greatkart.com',
                'company_phone': footer.phone if footer else '+880-123-456-789',
                'company_address': 'Dhaka, Bangladesh',
                'logo_url': logo_url
            }
        except Exception as e:
            logger.error(f"Error getting company info: {str(e)}")
            return {
                'company_name': 'GreatKart',
                'company_email': 'info@greatkart.com',
                'company_phone': '+880-123-456-789',
                'company_address': 'Dhaka, Bangladesh',
                'logo_url': None
            }
    
    @staticmethod
    def generate_invoice_html(order):
        """Generate invoice HTML for the order"""
        try:
            # Get invoice data
            invoice_data = InvoiceGenerator.get_invoice_data(order)
            
            # Render invoice template
            invoice_html = render_to_string(
                'invoice/invoice_template.html',
                invoice_data
            )
            
            return invoice_html
        except Exception as e:
            logger.error(f"Error generating invoice HTML: {str(e)}")
            return "<p>Invoice details could not be generated.</p>"
    
    @staticmethod
    def send_order_confirmation_email(order):
        """Send order confirmation email with invoice"""
        try:
            logger.info(f"Sending order confirmation email for order: {order.order_number}")
            
            # Get email settings
            email_settings = InvoiceEmailService.get_email_settings()
            if not email_settings:
                logger.error("No email settings found")
                return False
            
            # Get company info
            company_info = InvoiceEmailService.get_company_info()
            
            # Generate invoice HTML
            invoice_html = InvoiceEmailService.generate_invoice_html(order)
            
            # Prepare email context
            context = {
                'order_number': order.order_number,
                'customer_name': order.user.profile.full_name if hasattr(order.user, 'profile') and order.user.profile.full_name else order.user.email,
                'order_date': order.created_at.strftime('%B %d, %Y'),
                'order_status': order.get_status_display(),
                'total_amount': order.total_amount,
                'delivery_address': f"{order.delivery_address.address_line_1}, {order.delivery_address.city}, {order.delivery_address.country}" if order.delivery_address else "N/A",
                'invoice_html': invoice_html,
                **company_info
            }
            
            # Render email template
            email_html = render_to_string(
                'orders/order_confirmation.html',
                context
            )
            
            # Send email
            success = InvoiceEmailService._send_smtp_email(
                email_settings=email_settings,
                to_email=order.user.email,
                subject=f"Order Confirmation - {order.order_number}",
                html_content=email_html
            )
            
            if success:
                logger.info(f"Order confirmation email sent successfully to {order.user.email}")
            else:
                logger.error(f"Failed to send order confirmation email to {order.user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")
            return False
    
    @staticmethod
    def send_order_delivered_email(order):
        """Send order delivered email with invoice"""
        try:
            logger.info(f"Sending order delivered email for order: {order.order_number}")
            
            # Get email settings
            email_settings = InvoiceEmailService.get_email_settings()
            if not email_settings:
                logger.error("No email settings found")
                return False
            
            # Get company info
            company_info = InvoiceEmailService.get_company_info()
            
            # Generate invoice HTML
            invoice_html = InvoiceEmailService.generate_invoice_html(order)
            
            # Prepare email context
            context = {
                'order_number': order.order_number,
                'customer_name': order.user.profile.full_name if hasattr(order.user, 'profile') and order.user.profile.full_name else order.user.email,
                'order_date': order.created_at.strftime('%B %d, %Y'),
                'delivery_date': order.delivered_at.strftime('%B %d, %Y') if order.delivered_at else timezone.now().strftime('%B %d, %Y'),
                'order_status': order.get_status_display(),
                'total_amount': order.total_amount,
                'delivery_address': f"{order.delivery_address.address_line_1}, {order.delivery_address.city}, {order.delivery_address.country}" if order.delivery_address else "N/A",
                'invoice_html': invoice_html,
                **company_info
            }
            
            # Render email template
            email_html = render_to_string(
                'orders/order_delivered.html',
                context
            )
            
            # Send email
            success = InvoiceEmailService._send_smtp_email(
                email_settings=email_settings,
                to_email=order.user.email,
                subject=f"Order Delivered - {order.order_number}",
                html_content=email_html
            )
            
            if success:
                logger.info(f"Order delivered email sent successfully to {order.user.email}")
            else:
                logger.error(f"Failed to send order delivered email to {order.user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending order delivered email: {str(e)}")
            return False
    
    @staticmethod
    def _send_smtp_email(email_settings, to_email, subject, html_content):
        """Send email using SMTP settings"""
        try:
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{email_settings.from_name} <{email_settings.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Reply-To'] = email_settings.from_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP configuration
            smtp_server = email_settings.smtp_host
            smtp_port = email_settings.smtp_port
            smtp_username = email_settings.smtp_username
            smtp_password = email_settings.email_password
            
            # Create SMTP connection
            if email_settings.use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
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
