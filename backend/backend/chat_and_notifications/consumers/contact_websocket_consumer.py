"""
Contact Messages Real-time WebSocket Consumer
Handles WebSocket connections for Contact Messages real-time updates
"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class ContactWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for Contact Messages real-time updates
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contact_group_name = None
        self.user = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        print("🔍 DEBUG: Contact WebSocket consumer - connect() called")
        self.user = self.scope.get('user')
        print(f"🔍 DEBUG: Contact WebSocket user: {self.user}")
        
        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser) or not self.user:
            print("🔍 DEBUG: Contact WebSocket - user not authenticated, closing")
            await self.close()
            return
        
        # Check if user is staff/admin
        if not (self.user.is_staff or self.user.is_superuser):
            print("🔍 DEBUG: Contact WebSocket - user not staff/admin, closing")
            await self.close()
            return
        
        # Set contact group name
        self.contact_group_name = 'admin_contacts'
        print(f"🔍 DEBUG: Contact WebSocket - joining group: {self.contact_group_name}")
        
        # Join contact group
        await self.channel_layer.group_add(
            self.contact_group_name,
            self.channel_name
        )
        
        await self.accept()
        print("🔍 DEBUG: Contact WebSocket - connection accepted")
        
        # Send connection confirmation
        await self.send_json({
            'type': 'contact_connection_established',
            'user': self.user.email,
            'message': 'Connected to Contact Messages real-time updates'
        })
        print("🔍 DEBUG: Contact WebSocket - connection confirmation sent")
        
        # Send initial contact count
        await self.send_contact_count()
        print("🔍 DEBUG: Contact WebSocket - initial contact count sent")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave contact group
        if self.contact_group_name:
            try:
                await self.channel_layer.group_discard(
                    self.contact_group_name,
                    self.channel_name
                )
            except Exception:
                pass
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'get_contact_count':
            await self.send_contact_count()
        elif message_type == 'get_contact_stats':
            await self.send_contact_stats()
    
    async def new_contact(self, event):
        """Handle new contact message"""
        await self.send_json({
            'type': 'new_contact',
            'contact': event['contact']
        })
    
    async def contact_updated(self, event):
        """Handle contact message update"""
        await self.send_json({
            'type': 'contact_updated',
            'contact': event['contact']
        })
    
    async def contact_deleted(self, event):
        """Handle contact message deletion"""
        await self.send_json({
            'type': 'contact_deleted',
            'contact_id': event['contact_id']
        })
    
    async def contact_count_updated(self, event):
        """Handle contact count update"""
        print(f"🔍 DEBUG: Contact WebSocket consumer - contact_count_updated received: {event}")
        await self.send_json({
            'type': 'contact_count_updated',
            'unread_count': event['unread_count'],
            'total_count': event['total_count']
        })
        print("🔍 DEBUG: Contact WebSocket consumer - contact_count_updated sent to client")
    
    async def send_contact_count(self):
        """Send current contact count"""
        try:
            stats = await self.get_contact_stats()
            await self.send_json({
                'type': 'contact_count',
                'unread_count': stats['unread_count'],
                'total_count': stats['total_count']
            })
        except Exception as e:
            print(f"Error sending contact count: {e}")
    
    async def send_contact_stats(self):
        """Send detailed contact statistics"""
        try:
            stats = await self.get_contact_stats()
            await self.send_json({
                'type': 'contact_stats',
                'stats': stats
            })
        except Exception as e:
            print(f"Error sending contact stats: {e}")
    
    @database_sync_to_async
    def get_contact_stats(self):
        """Get contact statistics from database"""
        try:
            from chat_and_notifications.models.contact.contact import Contact
            
            total_count = Contact.objects.count()
            unread_count = Contact.objects.filter(is_read=False).count()
            replied_count = Contact.objects.filter(is_replied=True).count()
            
            return {
                'total_count': total_count,
                'unread_count': unread_count,
                'replied_count': replied_count,
                'read_count': total_count - unread_count
            }
        except Exception as e:
            print(f"Error getting contact stats: {e}")
            return {
                'total_count': 0,
                'unread_count': 0,
                'replied_count': 0,
                'read_count': 0
            }
