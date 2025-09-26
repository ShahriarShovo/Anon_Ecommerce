from django.db import models
from django.utils import timezone


class Logo(models.Model):
    """
    Model to store site logo information
    """
    name = models.CharField(max_length=100, default="Site Logo")
    logo_image = models.ImageField(upload_to='logos/', help_text="Upload site logo")
    is_active = models.BooleanField(default=True, help_text="Is this logo currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logo"
        verbose_name_plural = "Logos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
    
    @property
    def logo_url(self):
        """Return the URL of the logo image"""
        if self.logo_image:
            return self.logo_image.url
        return None
