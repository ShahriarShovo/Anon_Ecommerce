"""
Professional E-commerce Cart Models
===================================

This module contains the core cart functionality for a production-ready e-commerce system.
Designed for high performance and scalability.

Models:
- Cart: User's shopping cart session
- CartItem: Individual items in the cart with variants support
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from products.models import Product, ProductVariant

class Cart(models.Model):
    """
    Shopping Cart Model
    ===================
    
    Represents a user's shopping cart session. Each authenticated user has one cart,
    while guest users have temporary carts tied to their session.
    
    Features:
    - User association (authenticated users)
    - Session-based carts (guest users)
    - Automatic cleanup of old guest carts
    - Cart expiration for security
    """
    
    # User association - null for guest users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text="User who owns this cart (null for guest users)"
    )
    
    # Session key for guest users
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Session key for guest users"
    )
    
    # Cart metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the cart was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the cart was last updated"
    )
    
    # Cart status and expiration
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this cart is still active"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this cart expires (for guest users)"
    )
    
    # Cart totals (cached for performance)
    total_items = models.PositiveIntegerField(
        default=0,
        help_text="Total number of items in cart"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Subtotal before taxes and shipping"
    )
    
    class Meta:
        # Ensure one active cart per user/session
        unique_together = [
            ['user', 'is_active'],
            ['session_key', 'is_active']
        ]
        
        # Database indexes for performance
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key', 'is_active']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]
        
        # Ordering
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        else:
            return f"Guest Cart ({self.session_key[:8]}...)"
    
    def save(self, *args, **kwargs):
        """Override save to set expiration for guest carts"""
        if not self.user and not self.expires_at:
            # Guest carts expire after 30 days
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate and update cart totals"""
        items = self.items.all()
        
        total_items = sum(item.quantity for item in items)
        subtotal = sum(item.get_total_price() for item in items)
        
        self.total_items = total_items
        self.subtotal = subtotal
        self.save(update_fields=['total_items', 'subtotal', 'updated_at'])
        
        return {
            'total_items': total_items,
            'subtotal': subtotal
        }
    
    def is_expired(self):
        """Check if cart has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def clear_expired_items(self):
        """Remove items that are no longer available"""
        expired_items = []
        for item in self.items.all():
            if not item.is_available():
                expired_items.append(item)
        
        for item in expired_items:
            item.delete()
        
        if expired_items:
            self.calculate_totals()
        
        return len(expired_items)
    
    def is_empty(self):
        """Check if cart has no items"""
        return self.items.count() == 0
    
    def cleanup_if_empty(self):
        """Delete cart if it's empty (for both guest and authenticated users)"""
        if self.is_empty():
            if not self.user:
                # Delete guest carts when empty
                
                self.delete()
                return True
            else:
                # Delete authenticated user carts when empty (to prevent database bloat)
                
                self.delete()
                return True
        return False

class CartItem(models.Model):
    """
    Cart Item Model
    ===============
    
    Represents an individual item in a shopping cart. Supports both simple products
    and products with variants (size, color, etc.).
    
    Features:
    - Product and variant support
    - Quantity management
    - Price tracking (handles price changes)
    - Availability checking
    - Automatic cleanup
    """
    
    # Cart and product association
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Cart this item belongs to"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product being added to cart"
    )
    
    # Variant support (optional)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product variant (size, color, etc.)"
    )
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity of this item in cart"
    )
    
    # Price at time of adding to cart (for price change protection)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit when added to cart"
    )
    
    # Timestamps
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this item was added to cart"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this item was last updated"
    )
    
    class Meta:
        # Ensure unique product/variant combination per cart
        unique_together = [
            ['cart', 'product', 'variant']
        ]
        
        # Database indexes for performance
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['cart', 'variant']),
            models.Index(fields=['added_at']),
        ]
        
        # Ordering
        ordering = ['-added_at']
    
    def __str__(self):
        if self.variant:
            return f"{self.product.title} - {self.variant.title} (x{self.quantity})"
        else:
            return f"{self.product.title} (x{self.quantity})"
    
    def save(self, *args, **kwargs):
        """Override save method"""
        super().save(*args, **kwargs)
    
    def get_current_price(self):
        """Get current price of the product/variant"""
        if self.variant:
            return self.variant.price
        else:
            return self.product.price
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.unit_price * self.quantity
    
    def is_available(self):
        """Check if the product/variant is still available"""
        if not self.product.status == 'active':
            return False
        
        if self.variant:
            return self.variant.quantity >= self.quantity
        else:
            return self.product.quantity >= self.quantity
    
    def can_increase_quantity(self, amount=1):
        """Check if quantity can be increased"""
        if self.variant:
            return self.variant.quantity >= (self.quantity + amount)
        else:
            return self.product.quantity >= (self.quantity + amount)
    
    def increase_quantity(self, amount=1):
        """Increase quantity if possible"""
        if self.can_increase_quantity(amount):
            self.quantity += amount
            self.save(update_fields=['quantity', 'updated_at'])
            return True
        return False
    
    def decrease_quantity(self, amount=1):
        """Decrease quantity, remove item if quantity becomes 0"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save(update_fields=['quantity', 'updated_at'])
            return True
        else:
            # Remove item if quantity becomes 0 or less
            self.delete()
            return False
    
    def update_price(self):
        """Update unit price to current product price"""
        current_price = self.get_current_price()
        if current_price != self.unit_price:
            self.unit_price = current_price
            self.save(update_fields=['unit_price', 'updated_at'])
            return True
        return False
