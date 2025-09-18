from django.db import models
from products.models.products.product import Product
from products.models.products.variant import ProductVariant
from .order import Order


class OrderItem(models.Model):
    """
    Individual items within an order
    Represents each product/variant in the order
    """
    
    # Relationships
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Order this item belongs to"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        help_text="Product being ordered"
    )
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items',
        blank=True,
        null=True,
        help_text="Specific product variant (if applicable)"
    )
    
    # Item details
    quantity = models.PositiveIntegerField(
        help_text="Quantity of this item"
    )
    
    # Pricing (snapshot at time of order)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of order"
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total price for this item (quantity × unit_price)"
    )
    
    # Product details snapshot (in case product details change later)
    product_name = models.CharField(
        max_length=200,
        help_text="Product name at time of order"
    )
    
    product_sku = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Product SKU at time of order"
    )
    
    variant_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Variant title at time of order"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['created_at']
        unique_together = ['order', 'product', 'variant']
    
    def __str__(self):
        variant_info = f" ({self.variant_title})" if self.variant_title else ""
        return f"{self.product_name}{variant_info} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        
        # Store product details snapshot if not already set
        if not self.product_name:
            self.product_name = self.product.title
        
        if not self.product_sku:
            self.product_sku = getattr(self.product, 'sku', None)
        
        if self.variant and not self.variant_title:
            self.variant_title = str(self.variant)
        
        super().save(*args, **kwargs)
    
    def get_display_name(self):
        """Get display name for this order item"""
        if self.variant_title:
            return f"{self.product_name} - {self.variant_title}"
        return self.product_name
    
    def get_unit_price_display(self):
        """Get formatted unit price"""
        return f"৳{self.unit_price:,.2f}"
    
    def get_total_price_display(self):
        """Get formatted total price"""
        return f"৳{self.total_price:,.2f}"
