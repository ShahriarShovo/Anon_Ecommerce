from django.db import models
from django.utils import timezone


class Contact(models.Model):
    """
    Contact form submissions model
    """
    name = models.CharField(
        max_length=100,
        help_text='Contact person name'
    )
    email = models.EmailField(
        help_text='Contact person email'
    )
    subject = models.CharField(
        max_length=200,
        help_text='Contact subject'
    )
    message = models.TextField(
        help_text='Contact message'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Whether this contact message has been read'
    )
    is_replied = models.BooleanField(
        default=False,
        help_text='Whether this contact message has been replied'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"

    @property
    def is_new(self):
        """Check if this is a new unread message"""
        return not self.is_read

    @property
    def status(self):
        """Get the status of the contact message"""
        if self.is_replied:
            return 'Replied'
        elif self.is_read:
            return 'Read'
        else:
            return 'New'
