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
        # Only generate SKU if not already provided
        if not self.sku and hasattr(self, 'product') and self.product:
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
                # Generate unique SKU using microsecond timestamp and random number
                import time
                import random
                # Use microsecond timestamp for better uniqueness
                timestamp = str(int(time.time() * 1000000))[-8:]  # Last 8 digits of microsecond timestamp
                random_num = str(random.randint(1000, 9999))  # 4-digit random number
                self.sku = f"{base_sku}-{timestamp}{random_num}"
                
                # Ensure SKU is unique by checking database
                counter = 1
                original_sku = self.sku
                while ProductVariant.objects.filter(sku=self.sku).exists():
                    self.sku = f"{original_sku}-{counter}"
                    counter += 1
        
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
        """Get display price (old_price if available, otherwise price)"""
        return self.old_price if self.old_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if old_price is set"""
        if self.old_price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100, 2)
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
    
    def get_dynamic_options(self):
        """Get all dynamic options as a list of dictionaries"""
        return [
            {'name': option.name, 'value': option.value, 'position': option.position}
            for option in self.dynamic_options.all().order_by('position')
        ]
    
    def get_all_options(self):
        """Get all options (legacy + dynamic) as a list of dictionaries"""
        options = []
        
        # Add legacy options
        if self.option1_name and self.option1_value:
            options.append({'name': self.option1_name, 'value': self.option1_value, 'position': 1})
        if self.option2_name and self.option2_value:
            options.append({'name': self.option2_name, 'value': self.option2_value, 'position': 2})
        if self.option3_name and self.option3_value:
            options.append({'name': self.option3_name, 'value': self.option3_value, 'position': 3})
        
        # Add dynamic options
        dynamic_options = self.get_dynamic_options()
        for option in dynamic_options:
            options.append(option)
        
        return sorted(options, key=lambda x: x['position'])
    
    def set_dynamic_options(self, options_list):
        """Set dynamic options from a list of dictionaries"""
        print(f"Setting dynamic options for variant {self.id}: {options_list}")
        
        # Clear existing dynamic options
        self.dynamic_options.all().delete()
        
        # Deduplicate options based on name and value combination
        seen_options = set()
        unique_options = []
        
        for i, option in enumerate(options_list):
            if option.get('name') and option.get('value'):
                # Create a unique key for deduplication
                option_key = (option['name'], option['value'])
                
                if option_key not in seen_options:
                    seen_options.add(option_key)
                    unique_options.append(option)
                    print(f"Added unique option: name='{option['name']}', value='{option['value']}'")
                else:
                    print(f"Skipping duplicate option: name='{option['name']}', value='{option['value']}'")
        
        print(f"Unique options after deduplication: {len(unique_options)} out of {len(options_list)}")
        
        # Add unique options
        for i, option in enumerate(unique_options):
            print(f"Creating option: name='{option['name']}', value='{option['value']}', position={option.get('position', i + 1)}")
            try:
                self.dynamic_options.create(
                    name=option['name'],
                    value=option['value'],
                    position=option.get('position', i + 1)
                )
                print(f"Successfully created option")
            except Exception as e:
                print(f"Error creating option: {e}")
                raise
