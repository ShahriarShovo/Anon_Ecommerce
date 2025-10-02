"""
Contact Messages Real-time Signal Handlers
Handles WebSocket broadcasting for Contact model events
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat_and_notifications.models.contact.contact import Contact


@receiver(post_save, sender=Contact)
def contact_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler for Contact model save events
    Broadcasts real-time updates to admin WebSocket group
    """
    print(f"🔍 DEBUG: Contact signal triggered - created: {created}, contact: {instance.name}")
    print(f"🔍 DEBUG: Contact signal - instance.id: {instance.id}, is_read: {instance.is_read}")
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("🔍 DEBUG: Contact signal - no channel layer available")
            return
        
        print("🔍 DEBUG: Contact signal - channel layer available, proceeding...")

        # Prepare contact data for WebSocket broadcast
        contact_data = {
            'id': instance.id,
            'name': instance.name,
            'email': instance.email,
            'subject': instance.subject,
            'message': instance.message,
            'is_read': instance.is_read,
            'is_replied': instance.is_replied,
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
            'status': instance.status
        }

        # Determine event type
        event_type = 'new_contact' if created else 'contact_updated'
        print(f"🔍 DEBUG: Contact signal - broadcasting {event_type} to admin_contacts group")
        
        # Broadcast to admin group
        async_to_sync(channel_layer.group_send)(
            'admin_contacts',
            {
                'type': event_type,
                'contact': contact_data
            }
        )

        # Also broadcast contact count update
        unread_count = Contact.objects.filter(is_read=False).count()
        total_count = Contact.objects.count()
        print(f"🔍 DEBUG: Contact signal - broadcasting count update: unread={unread_count}, total={total_count}")
        
        async_to_sync(channel_layer.group_send)(
            'admin_contacts',
            {
                'type': 'contact_count_updated',
                'unread_count': unread_count,
                'total_count': total_count
            }
        )
        
        print("🔍 DEBUG: Contact signal - count update broadcasted successfully")

    except Exception as e:
        # Log error but don't crash the application
        print(f"Error broadcasting contact update: {e}")


@receiver(post_delete, sender=Contact)
def contact_deleted(sender, instance, **kwargs):
    """
    Signal handler for Contact model delete events
    Broadcasts real-time updates to admin WebSocket group
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        # Broadcast contact deletion
        async_to_sync(channel_layer.group_send)(
            'admin_contacts',
            {
                'type': 'contact_deleted',
                'contact_id': instance.id
            }
        )

        # Also broadcast contact count update
        async_to_sync(channel_layer.group_send)(
            'admin_contacts',
            {
                'type': 'contact_count_updated',
                'unread_count': Contact.objects.filter(is_read=False).count(),
                'total_count': Contact.objects.count()
            }
        )

    except Exception as e:
        # Log error but don't crash the application
        print(f"Error broadcasting contact deletion: {e}")
