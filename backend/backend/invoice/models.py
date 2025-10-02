from django.db import models
from orders.models.orders.order import Order

class Invoice(models.Model):
    """
    Invoice model for order invoices
    """
    
    # Invoice status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='invoice',
        help_text="Order this invoice is for"
    )
    
    # Invoice details
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique invoice number"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Invoice status"
    )
    
    # Invoice dates
    invoice_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when invoice was created"
    )
    
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Due date for payment"
    )
    
    # Company information
    company_name = models.CharField(
        max_length=200,
        default="Anon Ecommerce",
        help_text="Company name"
    )
    
    company_logo = models.URLField(
        blank=True,
        null=True,
        help_text="Company logo URL"
    )
    
    company_address = models.TextField(
        default="Dhaka, Bangladesh",
        help_text="Company address"
    )
    
    company_phone = models.CharField(
        max_length=20,
        default="+8801XXXXXXXXX",
        help_text="Company phone number"
    )
    
    company_email = models.EmailField(
        default="info@anonecommerce.com",
        help_text="Company email"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Set due date if not provided (30 days from invoice date)
        if not self.due_date and self.invoice_date:
            from datetime import timedelta
            self.due_date = self.invoice_date + timedelta(days=30)
        elif not self.due_date:
            # If invoice_date is None, set due_date to 30 days from now
            from datetime import datetime, timedelta
            self.due_date = datetime.now() + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import uuid
        import datetime
        
        # Format: INV-YYYYMMDD-XXXX
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:4].upper()
        return f"INV-{date_str}-{unique_id}"
    
    def get_total_amount(self):
        """Get total amount from order"""
        return self.order.total_amount
    
    def get_subtotal(self):
        """Get subtotal from order"""
        return self.order.subtotal
    
    def get_shipping_cost(self):
        """Get shipping cost from order"""
        return self.order.shipping_cost
    
    def get_tax_amount(self):
        """Get tax amount from order"""
        return self.order.tax_amount
    
    def get_invoice_date_display(self):
        """Get formatted invoice date"""
        return self.invoice_date.strftime('%d/%m/%Y')
    
    def get_due_date_display(self):
        """Get formatted due date"""
        if self.due_date:
            return self.due_date.strftime('%d/%m/%Y')
        return None
