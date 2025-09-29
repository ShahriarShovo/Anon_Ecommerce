from django.db import models
from django.utils import timezone


class FooterSettings(models.Model):
    """
    Main footer settings model
    """
    description = models.TextField(
        default='One of the biggest online shopping platform in Bangladesh.',
        help_text='Company description for footer'
    )
    copyright = models.CharField(
        max_length=200,
        default='© 2024 GreatKart. All rights reserved',
        help_text='Copyright text for footer'
    )
    email = models.EmailField(
        default='info@greatkart.com',
        help_text='Contact email for footer'
    )
    phone = models.CharField(
        max_length=20,
        default='+880-123-456-789',
        help_text='Contact phone for footer'
    )
    about_us = models.TextField(
        default='GreatKart is your one-stop destination for quality products at affordable prices. We are committed to providing excellent customer service and fast delivery across Bangladesh.',
        help_text='About us description'
    )
    mission = models.TextField(
        default='To provide the best online shopping experience with quality products, competitive prices, and excellent customer service.',
        help_text='Company mission statement'
    )
    vision = models.TextField(
        default='To become Bangladesh\'s leading e-commerce platform, connecting customers with quality products and services.',
        help_text='Company vision statement'
    )
    business_hours = models.TextField(
        default='Monday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: Closed',
        help_text='Business hours information'
    )
    quick_response = models.TextField(
        default='We typically respond to all inquiries within 24 hours during business days.',
        help_text='Quick response information'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this footer setting is active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Footer Setting'
        verbose_name_plural = 'Footer Settings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Footer Settings - {self.email}"


class SocialMediaLink(models.Model):
    """
    Social media links model - supports unlimited social links
    """
    footer_setting = models.ForeignKey(
        FooterSettings,
        on_delete=models.CASCADE,
        related_name='social_links',
        help_text='Footer setting this social link belongs to'
    )
    platform = models.CharField(
        max_length=50,
        help_text='Social media platform name (e.g., Facebook, Instagram)'
    )
    url = models.URLField(
        help_text='Social media profile URL'
    )
    icon = models.CharField(
        max_length=100,
        default='fab fa-link',
        help_text='FontAwesome icon class (e.g., fab fa-facebook-f)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this social link is active'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Social Media Link'
        verbose_name_plural = 'Social Media Links'
        ordering = ['order', 'platform']

    def __str__(self):
        return f"{self.platform} - {self.footer_setting.email}"
