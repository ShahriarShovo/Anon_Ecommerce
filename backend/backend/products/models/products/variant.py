from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal
from .product import Product

class ProductVariant(models.Model):
    # Basic Information
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=255, help_text="Variant title (e.g., 'Small - Red')")
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, null=True, help_text="Product barcode")
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Variant price"
    )
    old_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Old price (original price before discount)"
    )
    
    # Inventory
    quantity = models.PositiveIntegerField(default=0, help_text="Available quantity")
    track_quantity = models.BooleanField(default=True, help_text="Track inventory for this variant")
    allow_backorder = models.BooleanField(default=False, help_text="Allow backorder when out of stock")
    
    # Shopify-style Options (up to 3 options like Size, Color, Material)
    option1_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 1 name (e.g., Size)")
    option1_value = models.CharField(max_length=100, blank=True, null=True, help_text="Option 1 value (e.g., Small)")
    option2_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 2 name (e.g., Color)")
    option2_value = models.CharField(max_length=100, blank=True, null=True, help_text="Option 2 value (e.g., Red)")
    option3_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 3 name (e.g., Material)")
    option3_value = models.CharField(max_length=100, blank=True, null=True, help_text="Option 3 value (e.g., Cotton)")
    
    # Physical Properties
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Variant weight"
    )
    weight_unit = models.CharField(
        max_length=10,
        choices=[
            ('kg', 'Kilogram'),
            ('lb', 'Pound'),
            ('g', 'Gram'),
            ('oz', 'Ounce'),
        ],
        default='kg',
        help_text="Weight unit"
    )
    
    
    # Status
    position = models.PositiveIntegerField(default=1, help_text="Display position")
    is_active = models.BooleanField(default=True, help_text="Is this variant active?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        ordering = ['position', 'id']
        unique_together = ['product', 'option1_value', 'option2_value', 'option3_value']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate SKU from product title and variant options
            base_sku = slugify(self.product.title)[:10].upper()
            option_parts = []
            if self.option1_value:
                option_parts.append(slugify(self.option1_value)[:3].upper())
            if self.option2_value:
                option_parts.append(slugify(self.option2_value)[:3].upper())
            if self.option3_value:
                option_parts.append(slugify(self.option3_value)[:3].upper())
            
            if option_parts:
                self.sku = f"{base_sku}-{'-'.join(option_parts)}"
            else:
                self.sku = f"{base_sku}-{self.id or 'NEW'}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.title} - {self.title}"
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock"""
        if not self.track_quantity:
            return True
        return self.quantity > 0
    
    @property
    def display_price(self):
        """Get display price (compare_at_price if available, otherwise price)"""
        return self.compare_at_price if self.compare_at_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_at_price is set"""
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(((self.compare_at_price - self.price) / self.compare_at_price) * 100, 2)
        return 0
    
    def get_option_values(self):
        """Get all option values as a list"""
        options = []
        if self.option1_value:
            options.append(self.option1_value)
        if self.option2_value:
            options.append(self.option2_value)
        if self.option3_value:
            options.append(self.option3_value)
        return options
    
    def get_option_names(self):
        """Get all option names as a list"""
        names = []
        if self.option1_name:
            names.append(self.option1_name)
        if self.option2_name:
            names.append(self.option2_name)
        if self.option3_name:
            names.append(self.option3_name)
        return names
