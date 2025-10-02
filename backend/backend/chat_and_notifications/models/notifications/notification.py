# from django.db import models
# from django.contrib.auth import get_user_model
# from django.utils import timezone

# User = get_user_model()

# class Notification(models.Model):
#     NOTIFICATION_TYPES = [
#         ('general', 'General Notification'),
#         # ('promotion', 'Promotion'),
#         ('announcement', 'Announcement'),
#         ('maintenance', 'Maintenance'),
#         ('custom', 'Custom'),
#     ]
    
#     TARGET_TYPES = [
#         ('all', 'All Visitors'),
#         ('users', 'Registered Users Only'),
#         ('specific', 'Specific Users'),
#     ]
    
#     title = models.CharField(max_length=200)
#     message = models.TextField()
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
#     target_type = models.CharField(max_length=20, choices=TARGET_TYPES, default='all')
    
#     # For specific users targeting
#     target_users = models.ManyToManyField(User, blank=True, related_name='targeted_notifications')
    
#     # Display settings
#     is_active = models.BooleanField(default=True)
#     show_until = models.DateTimeField(null=True, blank=True)
#     priority = models.IntegerField(default=1, help_text="Higher number = higher priority")
    
#     # Tracking
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notifications')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Analytics
#     total_views = models.PositiveIntegerField(default=0)
#     unique_views = models.PositiveIntegerField(default=0)
    
#     class Meta:
#         ordering = ['-priority', '-created_at']
#         verbose_name = 'Notification'
#         verbose_name_plural = 'Notifications'
    
#     def __str__(self):
#         return f"{self.title} ({self.get_target_type_display()})"
    
#     def is_visible(self):
#         """Check if notification should be visible"""
#         if not self.is_active:
#             return False
        
#         if self.show_until and timezone.now() > self.show_until:
#             return False
            
#         return True

# class NotificationView(models.Model):
#     """Track individual views of notifications"""
#     notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='views')
#     session_key = models.CharField(max_length=40, help_text="Django session key for anonymous users")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_views')
#     viewed_at = models.DateTimeField(auto_now_add=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
    
#     class Meta:
#         unique_together = ['notification', 'session_key']
#         ordering = ['-viewed_at']
    
#     def __str__(self):
#         user_identifier = self.user.email if self.user else f"Session: {self.session_key[:8]}"
#         return f"{self.notification.title} - {user_identifier}"
