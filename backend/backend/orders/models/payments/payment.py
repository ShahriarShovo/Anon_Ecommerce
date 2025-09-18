from django.db import models
from django.utils import timezone
from .payment_method import PaymentMethod
from orders.models.orders.order import Order


class Payment(models.Model):
    """
    Payment model for storing payment information
    """
    
    # Payment status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Relationships
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        help_text="Order this payment is for"
    )
    
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments',
        help_text="Payment method used"
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Payment status"
    )
    
    # Transaction details
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="External transaction ID (from payment gateway)"
    )
    
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        help_text="Response from payment gateway"
    )
    
    # Cash on Delivery specific fields
    cod_collected = models.BooleanField(
        default=False,
        help_text="Whether COD amount was collected"
    )
    
    cod_collected_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When COD amount was collected"
    )
    
    cod_collected_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Who collected the COD amount"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When payment was completed"
    )
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for Order #{self.order.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Set cod_collected_at when COD is collected
        if self.cod_collected and not self.cod_collected_at:
            self.cod_collected_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_status_display_color(self):
        """Return color for status display"""
        status_colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'completed': '#10b981',
            'failed': '#ef4444',
            'cancelled': '#6b7280',
            'refunded': '#8b5cf6',
        }
        return status_colors.get(self.status, '#6b7280')
    
    def is_cash_on_delivery(self):
        """Check if this is a cash on delivery payment"""
        return self.payment_method.method_type == 'cash_on_delivery'
    
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.status == 'completed' and not self.is_cash_on_delivery()
    
    def get_amount_display(self):
        """Get formatted payment amount"""
        return f"৳{self.amount:,.2f}"
