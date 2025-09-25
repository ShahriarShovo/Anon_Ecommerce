from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    DELIVERY_STATUS = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    attachments = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='sent')
    is_read_by_recipient = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['delivery_status']),
        ]
    
    def __str__(self):
        return f"Message {self.id} - {self.sender.email} in Conversation {self.conversation.id}"
    
    def mark_as_read(self):
        """Mark message as read by recipient"""
        if not self.is_read_by_recipient:
            self.is_read_by_recipient = True
            self.read_at = timezone.now()
            self.delivery_status = 'read'
            self.save(update_fields=['is_read_by_recipient', 'read_at', 'delivery_status', 'updated_at'])
    
    def mark_as_delivered(self):
        """Mark message as delivered"""
        if self.delivery_status == 'sent':
            self.delivery_status = 'delivered'
            self.save(update_fields=['delivery_status', 'updated_at'])
    
    def save(self, *args, **kwargs):
        """Override save to update conversation's last_message_at"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update conversation's last message time
            self.conversation.update_last_message_time()
            
            # Increment unread count for the recipient
            is_staff_message = self.sender.is_staff or self.sender.is_superuser
            self.conversation.increment_unread_count(is_staff_message)
