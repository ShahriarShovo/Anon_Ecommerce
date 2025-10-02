from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_conversations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    unread_user_count = models.PositiveIntegerField(default=0)
    unread_staff_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['status', 'last_message_at']),
        ]
    
    def __str__(self):
        return f"Conversation {self.id} - {self.customer.email}"
    
    def update_last_message_time(self):
        """Update last_message_at when a new message is added"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at', 'updated_at'])
    
    def increment_unread_count(self, is_staff_message=False):
        """Increment unread count for the appropriate side"""
        if is_staff_message:
            self.unread_user_count += 1
        else:
            self.unread_staff_count += 1
        self.save(update_fields=['unread_user_count', 'unread_staff_count', 'updated_at'])
    
    def reset_unread_count(self, is_staff=False):
        """Reset unread count for the appropriate side"""
        if is_staff:
            self.unread_staff_count = 0
        else:
            self.unread_user_count = 0
        self.save(update_fields=['unread_user_count', 'unread_staff_count', 'updated_at'])
