from django.db import models
from django.core.validators import MinValueValidator
from .variant import ProductVariant

class VariantOption(models.Model):
    """Dynamic variant options for unlimited options support"""
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name='dynamic_options'
    )
    name = models.CharField(
        max_length=50, 
        help_text="Option name (e.g., Size, Color, Material)"
    )
    value = models.CharField(
        max_length=100, 
        help_text="Option value (e.g., Small, Red, Cotton)"
    )
    position = models.PositiveIntegerField(
        default=1, 
        help_text="Display position"
    )
    
    class Meta:
        verbose_name = "Variant Option"
        verbose_name_plural = "Variant Options"
        ordering = ['position', 'id']
        unique_together = ['variant', 'name', 'value']
        indexes = [
            models.Index(fields=['variant']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.variant.title} - {self.name}: {self.value}"
