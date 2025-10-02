from django.db import models
from django.utils import timezone
from accounts.models import User
from .address import Address

class Order(models.Model):
    """
    Main order model for storing customer orders
    """
    
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Order relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="User who placed the order"
    )
    
    # Order identification
    order_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique order number"
    )
    
    # Order status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current order status"
    )
    
    # Delivery information
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='orders',
        help_text="Delivery address for this order"
    )
    
    # Order amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Subtotal before tax and shipping"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Shipping cost"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Tax amount"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total order amount"
    )
    
    # Order notes and special instructions
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Special instructions or notes for this order"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Delivery tracking
    estimated_delivery = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Estimated delivery date"
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Actual delivery date"
    )
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calculate total if not set
        if not self.total_amount:
            # Handle None values
            subtotal = self.subtotal or 0
            shipping_cost = self.shipping_cost or 0
            tax_amount = self.tax_amount or 0
            self.total_amount = subtotal + shipping_cost + tax_amount
        
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        import uuid
        import datetime
        
        # Format: ORD-YYYYMMDD-XXXX
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:4].upper()
        return f"ORD-{date_str}-{unique_id}"
    
    def get_status_display_color(self):
        """Return color for status display"""
        status_colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'processing': '#8b5cf6',
            'shipped': '#06b6d4',
            'delivered': '#10b981',
            'cancelled': '#ef4444',
            'refunded': '#6b7280',
        }
        return status_colors.get(self.status, '#6b7280')
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def can_be_refunded(self):
        """Check if order can be refunded"""
        return self.status in ['delivered', 'shipped']
    
    def get_total_amount_display(self):
        """Get formatted total amount"""
        return f"৳{self.total_amount:,.2f}"
