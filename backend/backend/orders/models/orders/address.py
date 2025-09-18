from django.db import models
from accounts.models import User


class Address(models.Model):
    """
    User address model for storing delivery addresses
    Can be reused for multiple orders
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses',
        help_text="User who owns this address"
    )
    
    # Address fields
    full_name = models.CharField(
        max_length=100, 
        help_text="Full name for delivery"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Contact phone number"
    )
    city = models.CharField(
        max_length=50,
        help_text="City name"
    )
    address_line_1 = models.CharField(
        max_length=200,
        help_text="Primary address line"
    )
    address_line_2 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Secondary address line (optional)"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Postal/ZIP code"
    )
    country = models.CharField(
        max_length=50,
        default="Bangladesh",
        help_text="Country name"
    )
    
    # Address metadata
    is_default = models.BooleanField(
        default=False,
        help_text="Is this the default address for the user?"
    )
    address_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home'),
            ('office', 'Office'),
            ('other', 'Other'),
        ],
        default='home',
        help_text="Type of address"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset other default addresses for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
