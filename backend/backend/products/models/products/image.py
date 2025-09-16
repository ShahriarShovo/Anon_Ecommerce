from django.db import models
from django.core.validators import FileExtensionValidator

class ProductImage(models.Model):
    # Basic Information
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    
    # Image Details
    image = models.ImageField(
        upload_to='products/images/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text="Product image"
    )
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Alt text for accessibility")
    caption = models.CharField(max_length=255, blank=True, null=True, help_text="Image caption")
    
    # Display Properties
    position = models.PositiveIntegerField(default=1, help_text="Display position")
    is_primary = models.BooleanField(default=False, help_text="Is this the primary image?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['position', 'id']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['variant']),
            models.Index(fields=['is_primary']),
        ]
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.title} - Image {self.position}"
    
    @property
    def image_url(self):
        """Get the image URL"""
        if self.image:
            return self.image.url
        return None
