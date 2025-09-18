from django.db import models


class PaymentMethod(models.Model):
    """
    Payment method model for storing available payment options
    """
    
    # Payment method types
    METHOD_TYPE_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]
    
    # Basic information
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name for payment method"
    )
    
    method_type = models.CharField(
        max_length=20,
        choices=METHOD_TYPE_CHOICES,
        help_text="Type of payment method"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the payment method"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this payment method is available"
    )
    
    is_cod = models.BooleanField(
        default=False,
        help_text="Is this a cash on delivery method?"
    )
    
    # Payment gateway settings (for online payments)
    gateway_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Payment gateway name (for online payments)"
    )
    
    gateway_config = models.JSONField(
        blank=True,
        null=True,
        help_text="Gateway configuration settings"
    )
    
    # Fees and charges
    processing_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Processing fee for this payment method"
    )
    
    processing_fee_type = models.CharField(
        max_length=10,
        choices=[
            ('fixed', 'Fixed Amount'),
            ('percentage', 'Percentage'),
        ],
        default='fixed',
        help_text="Type of processing fee"
    )
    
    # Display settings
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying payment methods"
    )
    
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Icon class or URL for payment method"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-set is_cod based on method_type
        if self.method_type == 'cash_on_delivery':
            self.is_cod = True
        else:
            self.is_cod = False
        
        super().save(*args, **kwargs)
    
    def calculate_processing_fee(self, amount):
        """Calculate processing fee for given amount"""
        if self.processing_fee_type == 'percentage':
            return (amount * self.processing_fee) / 100
        return self.processing_fee
    
    def get_total_amount(self, order_amount):
        """Get total amount including processing fee"""
        fee = self.calculate_processing_fee(order_amount)
        return order_amount + fee
    
    @classmethod
    def get_active_methods(cls):
        """Get all active payment methods"""
        return cls.objects.filter(is_active=True).order_by('display_order', 'name')
    
    @classmethod
    def get_cod_method(cls):
        """Get cash on delivery payment method"""
        return cls.objects.filter(method_type='cash_on_delivery', is_active=True).first()
