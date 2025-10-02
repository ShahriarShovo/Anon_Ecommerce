from django.db import models
from django.utils import timezone
from PIL import Image
import os

# Import email models
from .email_model import EmailSettings, EmailTemplate, EmailLog

# Import footer models
from .footer_settings_model import FooterSettings, SocialMediaLink

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

class Banner(models.Model):
    """
    Model to store site banner information with auto resize functionality
    """
    name = models.CharField(max_length=100, default="Banner")
    banner_image = models.ImageField(upload_to='banners/', help_text="Upload banner image")
    is_active = models.BooleanField(default=True, help_text="Is this banner currently active?")
    display_order = models.PositiveIntegerField(default=0, help_text="Order of display (lower number = higher priority)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['display_order', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
    
    @property
    def banner_url(self):
        """Return the URL of the banner image"""
        if self.banner_image:
            return self.banner_image.url
        return None
    
    def save(self, *args, **kwargs):
        """Override save to auto resize banner to standard dimensions"""
        super().save(*args, **kwargs)
        
        if self.banner_image:
            # Standard banner dimensions (same as current banner)
            STANDARD_WIDTH = 1200
            STANDARD_HEIGHT = 400
            
            try:
                # Open the image
                img = Image.open(self.banner_image.path)
                
                # Resize image to standard dimensions
                img = img.resize((STANDARD_WIDTH, STANDARD_HEIGHT), Image.Resampling.LANCZOS)
                
                # Save the resized image
                img.save(self.banner_image.path, quality=85, optimize=True)

            except Exception as e:
                pass

    @classmethod
    def get_active_banners(cls):
        """Get all active banners ordered by display_order"""
        return cls.objects.filter(is_active=True).order_by('display_order')