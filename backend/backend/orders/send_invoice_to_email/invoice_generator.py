"""
Invoice Generator for Email Templates
====================================

This module generates invoice data and HTML for email templates.
"""

from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class InvoiceGenerator:
    """
    Generator for invoice data and HTML
    """
    
    @staticmethod
    def get_invoice_data(order):
        """Get invoice data for an order"""
        try:
            # Get order items
            order_items = order.items.all()
            
            # Get delivery address
            delivery_address = order.delivery_address
            
            # Get payment info
            payment = order.payment
            
            # Prepare invoice data
            invoice_data = {
                'order': order,
                'order_items': order_items,
                'delivery_address': delivery_address,
                'payment': payment,
                'invoice': {
                    'invoice_number': f"INV-{order.order_number}",
                    'invoice_date': order.created_at,
                    'due_date': order.created_at,  # Same as invoice date for now
                }
            }
            
            return invoice_data
            
        except Exception as e:
            logger.error(f"Error getting invoice data: {str(e)}")
            return {
                'order': order,
                'order_items': [],
                'delivery_address': None,
                'payment': None,
                'invoice': {
                    'invoice_number': f"INV-{order.order_number}",
                    'invoice_date': order.created_at,
                    'due_date': order.created_at,
                }
            }
    
    @staticmethod
    def generate_invoice_html(order):
        """Generate invoice HTML for email"""
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
            return f"<p>Invoice for order {order.order_number} could not be generated.</p>"
    
    @staticmethod
    def get_order_summary(order):
        """Get order summary for email templates"""
        try:
            return {
                'order_number': order.order_number,
                'order_date': order.created_at.strftime('%B %d, %Y'),
                'total_amount': order.total_amount,
                'subtotal': order.subtotal,
                'shipping_cost': order.shipping_cost,
                'tax_amount': order.tax_amount,
                'status': order.get_status_display(),
                'item_count': order.items.count()
            }
        except Exception as e:
            logger.error(f"Error getting order summary: {str(e)}")
            return {
                'order_number': order.order_number,
                'order_date': 'N/A',
                'total_amount': 0,
                'subtotal': 0,
                'shipping_cost': 0,
                'tax_amount': 0,
                'status': 'Unknown',
                'item_count': 0
            }
