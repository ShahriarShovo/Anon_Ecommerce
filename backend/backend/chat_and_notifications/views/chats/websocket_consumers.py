import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from ...models import Conversation, Message, Participant

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for individual conversation chat"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        print(f"WebSocket connection attempt - User: {self.scope.get('user')}")
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        # Get user from scope
        self.user = self.scope.get('user')
        
        print(f"WebSocket user authentication check - User: {self.user}, Is Anonymous: {isinstance(self.user, AnonymousUser)}")
        
        if isinstance(self.user, AnonymousUser) or not self.user:
            print("WebSocket connection rejected - User not authenticated")
            await self.close()
            return
        
        # Verify user has access to this conversation
        if not await self.verify_conversation_access():
            await self.close()
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user's online status
        await self.update_online_status(True)
        
        # Send connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'conversation_id': self.conversation_id,
            'user': self.user.email
        })
        
        print(f"WebSocket connection established for user: {self.user.email}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Update user's online status
        await self.update_online_status(False)
        
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(content)
        elif message_type == 'typing_start':
            await self.handle_typing_start(content)
        elif message_type == 'typing_stop':
            await self.handle_typing_stop(content)
        elif message_type == 'mark_read':
            await self.handle_mark_read(content)
    
    async def handle_chat_message(self, content):
        """Handle chat message"""
        message_content = content.get('message', '').strip()
        print(f"WebSocket received message: {message_content}")
        
        if not message_content:
            await self.send_json({
                'type': 'error',
                'message': 'Message content cannot be empty'
            })
            return
        
        # Save message to database
        message = await self.save_message(message_content)
        print(f"Message saved to database: {message}")
        
        if message:
            # Send message to conversation group (including sender)
            message_data = {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.email,
                'sender_name': getattr(message.sender, 'full_name', None) or message.sender.email,
                'created_at': message.created_at.isoformat(),
                'message_type': message.message_type,
                'is_sender_staff': message.sender.is_staff or message.sender.is_superuser,
                'conversation_id': str(message.conversation_id),
            }
            
            print(f"Sending message to group: {message_data}")
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

            # Also notify admin inbox group for real-time list updates
            try:
                await self.channel_layer.group_send(
                    'admin_inbox',
                    {
                        'type': 'new_message',
                        'message': message_data
                    }
                )
            except Exception as e:
                # Avoid crashing the consumer if admin group not present
                print(f"Warning: failed to notify admin_inbox group: {e}")
    
    async def handle_typing_start(self, content):
        """Handle typing start indicator"""
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_start',
                'user': self.user.email,
                'user_name': self.user.full_name or self.user.email
            }
        )
    
    async def handle_typing_stop(self, content):
        """Handle typing stop indicator"""
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_stop',
                'user': self.user.email
            }
        )
    
    async def handle_mark_read(self, content):
        """Handle mark messages as read"""
        message_ids = content.get('message_ids', [])
        
        if message_ids:
            await self.mark_messages_read(message_ids)
            
            # Notify other participants
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'messages_read',
                    'user': self.user.email,
                    'message_ids': message_ids
                }
            )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send_json({
            'type': 'chat_message',
            'message': event['message']
        })
    
    async def typing_start(self, event):
        """Send typing start to WebSocket"""
        if event['user'] != self.user.email:
            await self.send_json({
                'type': 'typing_start',
                'user': event['user'],
                'user_name': event['user_name']
            })
    
    async def typing_stop(self, event):
        """Send typing stop to WebSocket"""
        if event['user'] != self.user.email:
            await self.send_json({
                'type': 'typing_stop',
                'user': event['user']
            })
    
    async def messages_read(self, event):
        """Send messages read notification to WebSocket"""
        if event['user'] != self.user.email:
            await self.send_json({
                'type': 'messages_read',
                'user': event['user'],
                'message_ids': event['message_ids']
            })
    
    @database_sync_to_async
    def verify_conversation_access(self):
        """Verify user has access to this conversation"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return (
                conversation.customer == self.user or 
                conversation.assigned_to == self.user or
                self.user.is_staff or 
                self.user.is_superuser
            )
        except ObjectDoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
                message_type='text'
            )
            return message
        except ObjectDoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            messages = Message.objects.filter(
                id__in=message_ids,
                conversation=conversation
            )
            
            for message in messages:
                if not message.is_read_by_recipient:
                    message.mark_as_read()
            
            # Reset unread count for this user
            if self.user.is_staff or self.user.is_superuser:
                conversation.reset_unread_count(is_staff=True)
            else:
                conversation.reset_unread_count(is_staff=False)
                
        except ObjectDoesNotExist:
            pass
    
    @database_sync_to_async
    def update_online_status(self, is_online):
        """Update user's online status"""
        if not self.user or self.user.is_anonymous:
            return
            
        participants = Participant.objects.filter(
            user_id=self.user.id,
            is_active=True
        )
        
        for participant in participants:
            participant.set_online_status(is_online)


class AdminConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for admin/staff inbox"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check if user is staff/admin
        if not (self.user.is_staff or self.user.is_superuser):
            await self.close()
            return
        
        self.admin_group_name = 'admin_inbox'
        
        # Join admin group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user's online status
        await self.update_online_status(True)
        
        # Send connection confirmation
        await self.send_json({
            'type': 'admin_connection_established',
            'user': self.user.email
        })
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Update user's online status
        await self.update_online_status(False)
        
        # Leave admin group
        await self.channel_layer.group_discard(
            self.admin_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'get_stats':
            await self.send_stats()
        elif message_type == 'get_online_users':
            await self.send_online_users()
    
    async def new_conversation(self, event):
        """Send new conversation notification"""
        await self.send_json({
            'type': 'new_conversation',
            'conversation': event['conversation']
        })
    
    async def conversation_updated(self, event):
        """Send conversation update notification"""
        await self.send_json({
            'type': 'conversation_updated',
            'conversation': event['conversation']
        })
    
    async def new_message(self, event):
        """Send new message notification"""
        await self.send_json({
            'type': 'new_message',
            'message': event['message']
        })
    
    async def user_online_status(self, event):
        """Send user online status update"""
        await self.send_json({
            'type': 'user_online_status',
            'user': event['user'],
            'is_online': event['is_online']
        })
    
    async def send_stats(self):
        """Send inbox statistics"""
        stats = await self.get_inbox_stats()
        await self.send_json({
            'type': 'inbox_stats',
            'stats': stats
        })
    
    async def send_online_users(self):
        """Send online users list"""
        online_users = await self.get_online_users()
        await self.send_json({
            'type': 'online_users',
            'users': online_users
        })
    
    @database_sync_to_async
    def get_inbox_stats(self):
        """Get inbox statistics"""
        return {
            'total_conversations': Conversation.objects.count(),
            'open_conversations': Conversation.objects.filter(status='open').count(),
            'unread_conversations': Conversation.objects.filter(unread_staff_count__gt=0).count(),
            'assigned_to_me': Conversation.objects.filter(assigned_to=self.user).count()
        }
    
    @database_sync_to_async
    def get_online_users(self):
        """Get online users"""
        online_participants = Participant.objects.filter(
            is_online=True,
            is_active=True
        ).select_related('user')
        
        return [
            {
                'id': p.user.id,
                'email': p.user.email,
                'full_name': p.user.full_name,
                'is_staff': p.user.is_staff,
                'last_seen': p.last_seen_at.isoformat()
            }
            for p in online_participants
        ]
    
    @database_sync_to_async
    def update_online_status(self, is_online):
        """Update user's online status"""
        if not self.user or self.user.is_anonymous:
            return
            
        participants = Participant.objects.filter(
            user_id=self.user.id,
            is_active=True
        )
        
        for participant in participants:
            participant.set_online_status(is_online)
