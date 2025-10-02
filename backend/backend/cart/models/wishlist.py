"""
Wishlist Models
===============

This module contains wishlist functionality for the e-commerce system.
Allows users to save products for later purchase.

Models:
- Wishlist: User's wishlist collection
- WishlistItem: Individual items in the wishlist
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product, ProductVariant

class Wishlist(models.Model):
    """
    Wishlist Model
    ==============
    
    Represents a user's wishlist for saving products they want to buy later.
    Only authenticated users can have wishlists.
    
    Features:
    - User-specific wishlists
    - Product and variant support
    - Automatic cleanup
    """
    
    # User association (required for wishlists)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists',
        help_text="User who owns this wishlist"
    )
    
    # Wishlist metadata
    name = models.CharField(
        max_length=100,
        default="My Wishlist",
        help_text="Name of the wishlist"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the wishlist was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the wishlist was last updated"
    )
    
    # Wishlist status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this wishlist is still active"
    )
    
    class Meta:
        # Ensure one active wishlist per user
        unique_together = [
            ['user', 'is_active']
        ]
        
        # Database indexes for performance
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        
        # Ordering
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    def get_total_items(self):
        """Get total number of items in wishlist"""
        return self.items.count()
    
    def clear_unavailable_items(self):
        """Remove items that are no longer available"""
        unavailable_items = []
        for item in self.items.all():
            if not item.is_available():
                unavailable_items.append(item)
        
        for item in unavailable_items:
            item.delete()
        
        return len(unavailable_items)

class WishlistItem(models.Model):
    """
    Wishlist Item Model
    ===================
    
    Represents an individual item in a user's wishlist.
    Supports both simple products and products with variants.
    
    Features:
    - Product and variant support
    - Availability checking
    - Automatic cleanup
    """
    
    # Wishlist and product association
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Wishlist this item belongs to"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product in wishlist"
    )
    
    # Variant support (optional)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product variant (size, color, etc.)"
    )
    
    # Timestamps
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this item was added to wishlist"
    )
    
    class Meta:
        # Ensure unique product/variant combination per wishlist
        unique_together = [
            ['wishlist', 'product', 'variant']
        ]
        
        # Database indexes for performance
        indexes = [
            models.Index(fields=['wishlist', 'product']),
            models.Index(fields=['wishlist', 'variant']),
            models.Index(fields=['added_at']),
        ]
        
        # Ordering
        ordering = ['-added_at']
    
    def __str__(self):
        if self.variant:
            return f"{self.product.title} - {self.variant.title}"
        else:
            return f"{self.product.title}"
    
    def is_available(self):
        """Check if the product/variant is still available"""
        if not self.product.status == 'active':
            return False
        
        if self.variant:
            return self.variant.quantity > 0
        else:
            return self.product.quantity > 0
    
    def get_current_price(self):
        """Get current price of the product/variant"""
        if self.variant:
            return self.variant.price
        else:
            return self.product.price
