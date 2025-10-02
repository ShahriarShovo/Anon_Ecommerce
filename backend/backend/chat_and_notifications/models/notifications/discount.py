# from django.db import models
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from django.core.validators import MinValueValidator, MaxValueValidator

# User = get_user_model()

# class Discount(models.Model):
#     DISCOUNT_TYPES = [
#         ('general', 'General Discount (All Products)'),
#         ('quantity', 'Quantity-based Discount'),
#         ('product_specific', 'Product-specific Discount'),
#         ('category', 'Category Discount'),
#     ]
    
#     STATUS_CHOICES = [
#         ('active', 'Active'),
#         ('inactive', 'Inactive'),
#         ('expired', 'Expired'),
#     ]
    
#     # Basic Information
#     name = models.CharField(max_length=200, help_text="Discount name/description")
#     discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='general')
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
#     # Discount Details
#     percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         help_text="Discount percentage (0-100)"
#     )
#     minimum_amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=0,
#         help_text="Minimum cart amount to apply discount"
#     )
#     maximum_discount_amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         null=True, 
#         blank=True,
#         help_text="Maximum discount amount (optional)"
#     )
    
#     # Quantity-based discount settings
#     minimum_quantity = models.PositiveIntegerField(
#         default=1,
#         help_text="Minimum quantity required for quantity-based discounts"
#     )
    
#     # Time-based settings
#     valid_from = models.DateTimeField(default=timezone.now)
#     valid_until = models.DateTimeField(null=True, blank=True)
    
#     # Target settings
#     target_products = models.ManyToManyField(
#         'products.Product', 
#         blank=True, 
#         related_name='discounts',
#         help_text="Specific products for product-specific discounts"
#     )
#     target_categories = models.ManyToManyField(
#         'products.Category', 
#         blank=True, 
#         related_name='discounts',
#         help_text="Categories for category-based discounts"
#     )
    
#     # Usage limits
#     usage_limit = models.PositiveIntegerField(
#         null=True, 
#         blank=True,
#         help_text="Maximum number of times this discount can be used"
#     )
#     usage_count = models.PositiveIntegerField(default=0)
    
#     # Admin settings
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_discounts')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Display settings
#     show_in_notifications = models.BooleanField(default=True, help_text="Show in notification modal")
#     notification_message = models.TextField(
#         blank=True, 
#         help_text="Custom message to show in notifications"
#     )
    
#     # Display options
#     DISPLAY_TYPES = [
#         ('modal', 'Modal Popup'),
#         ('image', 'Image Banner'),
#         ('both', 'Both Modal and Image'),
#     ]
    
#     display_type = models.CharField(
#         max_length=10, 
#         choices=DISPLAY_TYPES, 
#         default='modal',
#         help_text="How to display the discount notification"
#     )
    
#     # Image settings
#     discount_image = models.ImageField(
#         upload_to='discounts/images/', 
#         blank=True, 
#         null=True,
#         help_text="Discount banner image"
#     )
#     image_alt_text = models.CharField(
#         max_length=200, 
#         blank=True,
#         help_text="Alt text for discount image"
#     )
    
#     # Modal settings
#     modal_title = models.CharField(
#         max_length=200, 
#         blank=True,
#         help_text="Modal title (if different from name)"
#     )
#     modal_button_text = models.CharField(
#         max_length=50, 
#         default='Shop Now',
#         help_text="Button text in modal"
#     )
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Discount'
#         verbose_name_plural = 'Discounts'
    
#     def __str__(self):
#         return f"{self.name} ({self.percentage}%)"
    
#     def is_valid(self):
#         """Check if discount is currently valid"""
#         now = timezone.now()
        
#         # Check status
#         if self.status != 'active':
#             return False
        
#         # Check time validity
#         if now < self.valid_from:
#             return False
        
#         if self.valid_until and now > self.valid_until:
#             return False
        
#         # Check usage limit
#         if self.usage_limit and self.usage_count >= self.usage_limit:
#             return False
        
#         return True
    
#     def can_apply_to_cart(self, cart_items, user=None):
#         """Check if discount can be applied to current cart"""
#         if not self.is_valid():
#             return False, "Discount is not valid"
        
#         # Check minimum amount
#         cart_total = sum(item.get('total', 0) for item in cart_items)
        
#         if cart_total < self.minimum_amount:
#             return False, f"Minimum cart amount of {self.minimum_amount} required"
        
#         # Check quantity for quantity-based discounts
#         if self.discount_type == 'quantity':
#             total_quantity = sum(item.get('quantity', 0) for item in cart_items)
#             if total_quantity < self.minimum_quantity:
#                 return False, f"Minimum {self.minimum_quantity} items required"
        
#         # Check product-specific discounts
#         if self.discount_type == 'product_specific':
#             cart_product_ids = [item.get('product_id', 0) for item in cart_items]
#             target_product_ids = list(self.target_products.values_list('id', flat=True))
#             if not any(pid in target_product_ids for pid in cart_product_ids):
#                 return False, "Required products not in cart"
        
#         return True, "Valid"
    
#     def calculate_discount_amount(self, cart_items):
#         """Calculate discount amount for given cart items"""
#         if not self.is_valid():
#             return 0
        
#         # Get applicable items based on discount type
#         applicable_items = []
        
#         if self.discount_type == 'general':
#             applicable_items = cart_items
#         elif self.discount_type == 'quantity':
#             applicable_items = cart_items
#         elif self.discount_type == 'product_specific':
#             target_product_ids = list(self.target_products.values_list('id', flat=True))
#             applicable_items = [item for item in cart_items if item.get('product_id', 0) in target_product_ids]
#         elif self.discount_type == 'category':
#             target_category_ids = list(self.target_categories.values_list('id', flat=True))
#             # For now, we'll use all items for category discounts since we don't have category info in cart_items
#             applicable_items = cart_items
        
#         # Calculate total amount for applicable items
#         total_amount = sum(item.get('total', 0) for item in applicable_items)
        
#         # Calculate discount amount
#         discount_amount = (total_amount * self.percentage) / 100
        
#         # Apply maximum discount limit if set
#         if self.maximum_discount_amount:
#             discount_amount = min(discount_amount, self.maximum_discount_amount)
        
#         return round(discount_amount, 2)
    
#     def increment_usage(self):
#         """Increment usage count"""
#         self.usage_count += 1
#         self.save(update_fields=['usage_count'])

# class DiscountUsage(models.Model):
#     """Track individual discount usage"""
#     discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='usages')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='discount_usages')
#     session_key = models.CharField(max_length=40, help_text="Session key for anonymous users")
#     order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
#     discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     used_at = models.DateTimeField(auto_now_add=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
    
#     class Meta:
#         ordering = ['-used_at']
#         unique_together = ['discount', 'session_key', 'order']
    
#     def __str__(self):
#         user_identifier = self.user.email if self.user else f"Session: {self.session_key[:8]}"
#         return f"{self.discount.name} - {user_identifier} - {self.discount_amount}"
