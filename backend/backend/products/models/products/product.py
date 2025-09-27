from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from ..category.category import Category
from ..category.sub_category import SubCategory

class Product(models.Model):
    # Basic Information
    title = models.CharField(max_length=255, help_text="Product title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL-friendly version of title")
    description = models.TextField(blank=True, null=True, help_text="Product description")
    short_description = models.TextField(max_length=500, blank=True, null=True, help_text="Brief product description")
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO meta title")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO meta description")
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Product Type & Status
    product_type = models.CharField(
        max_length=20,
        choices=[
            ('simple', 'Simple'),
            ('variable', 'Variable'),
        ],
        default='simple',
        help_text="Product type"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ],
        default='draft',
        help_text="Product status"
    )
    
    # Shopify-style Variant Options
    option1_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 1 name (e.g., Size)")
    option2_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 2 name (e.g., Color)")
    option3_name = models.CharField(max_length=50, blank=True, null=True, help_text="Option 3 name (e.g., Material)")
    
    # Pricing (for simple products)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Product price"
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
    track_quantity = models.BooleanField(default=True, help_text="Track inventory for this product")
    quantity = models.PositiveIntegerField(default=0, help_text="Available quantity")
    allow_backorder = models.BooleanField(default=False, help_text="Allow backorder when out of stock")
    quantity_policy = models.CharField(
        max_length=20,
        choices=[
            ('deny', 'Deny'),
            ('continue', 'Continue'),
        ],
        default='deny',
        help_text="What to do when quantity is 0"
    )
    
    # Physical Properties
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Product weight"
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
    
    # Shipping
    requires_shipping = models.BooleanField(default=True, help_text="This product requires shipping")
    taxable = models.BooleanField(default=True, help_text="This product is taxable")
    
    # SEO & Marketing
    featured = models.BooleanField(default=False, help_text="Feature this product")
    tags = models.TextField(blank=True, null=True, help_text="Product tags (comma-separated)")
    
    # Default Variant (for variable products)
    default_variant = models.ForeignKey(
        'ProductVariant', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='default_for_product',
        help_text="Default variant for variable products"
    )
    default_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Default variant price (cached for performance)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, help_text="When product was published")
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def is_variable(self):
        """Check if product has variants"""
        return self.variants.exists()
    
    @property
    def min_price(self):
        """Get minimum price from variants or product price"""
        if self.is_variable:
            return self.variants.aggregate(min_price=models.Min('price'))['min_price']
        return self.price
    
    @property
    def max_price(self):
        """Get maximum price from variants or product price"""
        if self.is_variable:
            return self.variants.aggregate(max_price=models.Max('price'))['max_price']
        return self.price
    
    @property
    def total_inventory(self):
        """Get total inventory from variants or product quantity"""
        if self.is_variable:
            return self.variants.aggregate(total=models.Sum('quantity'))['total'] or 0
        return self.quantity
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if self.is_variable:
            return self.variants.filter(quantity__gt=0).exists()
        return self.quantity > 0
    
    @property
    def primary_image(self):
        """Get the primary image or first image"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()
    
    def set_default_variant(self, variant=None):
        """Set default variant for variable products"""
        if self.product_type != 'variable':
            return False
        
        if variant is None:
            # Set first active variant as default
            variant = self.variants.filter(is_active=True).first()
        
        if variant and variant.product == self:
            self.default_variant = variant
            self.default_price = variant.price
            self.save(update_fields=['default_variant', 'default_price'])
            return True
        return False
    
    def get_display_price(self):
        """Get display price for product (default variant price for variable products)"""
        if self.product_type == 'variable':
            if self.default_variant and self.default_price:
                return self.default_price
            # Fallback: get first variant price if default not set
            first_variant = self.variants.filter(is_active=True).first()
            if first_variant:
                return first_variant.price
        return self.price
    
    def get_display_old_price(self):
        """Get display old price for product (default variant old price for variable products)"""
        if self.product_type == 'variable':
            if self.default_variant:
                return self.default_variant.old_price
            # Fallback: get first variant old price if default not set
            first_variant = self.variants.filter(is_active=True).first()
            if first_variant:
                return first_variant.old_price
        return self.old_price
    
    def is_default_variant_in_stock(self):
        """Check if default variant is in stock"""
        if self.product_type == 'variable':
            if self.default_variant:
                return self.default_variant.quantity > 0
            # Fallback: check first variant stock if default not set
            first_variant = self.variants.filter(is_active=True).first()
            if first_variant:
                return first_variant.quantity > 0
        return self.is_in_stock
