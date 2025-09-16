from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductReview(models.Model):
    # Basic Information
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
    # Review Content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Review title")
    comment = models.TextField(help_text="Review comment")
    
    # User Information (for guest reviews)
    user_name = models.CharField(max_length=100, blank=True, null=True, help_text="User name for guest reviews")
    user_email = models.EmailField(blank=True, null=True, help_text="User email for guest reviews")
    
    # Review Status
    is_approved = models.BooleanField(default=False, help_text="Is this review approved?")
    is_verified_purchase = models.BooleanField(default=False, help_text="Is this a verified purchase?")
    
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0, help_text="Number of helpful votes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        user_display = self.user_name or (self.user.username if self.user else 'Anonymous')
        return f"{self.product.title} - {user_display} - {self.rating} stars"
    
    @property
    def display_name(self):
        """Get display name for the reviewer"""
        if self.user and self.user.full_name:
            return self.user.full_name
        elif self.user:
            return self.user.username
        elif self.user_name:
            return self.user_name
        else:
            return 'Anonymous'


class ReviewVote(models.Model):
    """Model for tracking helpful votes on reviews"""
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    is_helpful = models.BooleanField(default=True, help_text="Is this vote helpful?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Review Vote"
        verbose_name_plural = "Review Votes"
        unique_together = ['review', 'user']
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.review.product.title} - {'Helpful' if self.is_helpful else 'Not Helpful'}"
