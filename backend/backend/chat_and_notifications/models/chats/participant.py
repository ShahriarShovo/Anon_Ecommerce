from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Participant(models.Model):
    """Track participant information for conversations"""
    
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['conversation', 'user']
        ordering = ['-last_seen_at']
        indexes = [
            models.Index(fields=['user', 'is_online']),
            models.Index(fields=['conversation', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} in Conversation {self.conversation.id}"
    
    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen_at = timezone.now()
        self.save(update_fields=['last_seen_at'])
    
    def set_online_status(self, is_online):
        """Set online status"""
        self.is_online = is_online
        self.save(update_fields=['is_online', 'last_seen_at'])
    
    def deactivate(self):
        """Deactivate participant"""
        self.is_active = False
        self.is_online = False
        self.save(update_fields=['is_active', 'is_online'])
