import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ...models.orders.order import Order

User = get_user_model()

class OrderWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time order management"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_group_name = None
        self.user = None
    
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
        
        self.order_group_name = 'admin_orders'
        
        # Join admin orders group
        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name
        )
        
        await self.accept()

        # Send connection confirmation
        await self.send_json({
            'type': 'order_connection_established',
            'user': self.user.email
        })
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave admin orders group
        if getattr(self, 'order_group_name', None):
            try:
                await self.channel_layer.group_discard(
                    self.order_group_name,
                    self.channel_name
                )
            except Exception:
                # Silently ignore if group cleanup fails
                pass
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'get_order_stats':
            await self.send_order_stats()
        elif message_type == 'get_pending_orders':
            await self.send_pending_orders()
    
    async def order_stats(self, event):
        """Handle order stats group message"""
        await self.send_json({
            'type': 'order_stats',
            'stats': event['stats']
        })
    
    async def new_order(self, event):
        """Send new order notification"""
        await self.send_json({
            'type': 'new_order',
            'order': event['order']
        })
    
    async def order_updated(self, event):
        """Send order update notification"""
        await self.send_json({
            'type': 'order_updated',
            'order': event['order']
        })
    
    async def order_status_changed(self, event):
        """Send order status change notification"""
        await self.send_json({
            'type': 'order_status_changed',
            'order': event['order']
        })
    
    async def send_order_stats(self):
        """Send order statistics"""
        stats = await self.get_order_stats()
        await self.send_json({
            'type': 'order_stats',
            'stats': stats
        })
    
    async def send_pending_orders(self):
        """Send pending orders list"""
        orders = await self.get_pending_orders()
        await self.send_json({
            'type': 'pending_orders',
            'orders': orders
        })
    
    @database_sync_to_async
    def get_order_stats(self):
        """Get order statistics"""
        return {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'processing_orders': Order.objects.filter(status='processing').count(),
            'shipped_orders': Order.objects.filter(status='shipped').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        }
    
    @database_sync_to_async
    def get_pending_orders(self):
        """Get pending orders"""
        orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
        result = []
        for order in orders:
            user_name = order.user.email
            try:
                if hasattr(order.user, 'profile') and order.user.profile.full_name:
                    user_name = order.user.profile.full_name
            except:
                pass
            
            result.append({
                'id': order.id,
                'order_number': order.order_number,
                'user_email': order.user.email,
                'user_name': user_name,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'delivery_address': {
                    'address_line_1': order.delivery_address.address_line_1,
                    'city': order.delivery_address.city,
                    'postal_code': order.delivery_address.postal_code,
                } if order.delivery_address else None
            })
        return result

# Order model signals for real-time notifications
@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance, created, **kwargs):
    """Signal handler for order create/update"""

    from channels.layers import get_channel_layer
    import asyncio
    
    channel_layer = get_channel_layer()
    if not channel_layer:

        return
    
    # Prepare order data
    user_name = instance.user.email
    try:
        if hasattr(instance.user, 'profile') and instance.user.profile.full_name:
            user_name = instance.user.profile.full_name
    except:
        pass
    
    order_data = {
        'id': instance.id,
        'order_number': instance.order_number,
        'user_email': instance.user.email,
        'user_name': user_name,
        'total_amount': float(instance.total_amount),
        'status': instance.status,
        'created_at': instance.created_at.isoformat(),
        'delivery_address': {
            'address_line_1': instance.delivery_address.address_line_1,
            'city': instance.delivery_address.city,
            'postal_code': instance.delivery_address.postal_code,
        } if instance.delivery_address else None
    }
    
    # Get updated order stats (ultra-optimized - only pending count for speed)
    pending_count = Order.objects.filter(status='pending').count()
    
    stats = {
        'pending_orders': pending_count,
        'total_orders': Order.objects.count(),  # Only if needed
    }
    
    # Send to admin orders group
    async def send_notification():

        if created:
            await channel_layer.group_send(
                'admin_orders',
                {
                    'type': 'new_order',
                    'order': order_data
                }
            )
        else:
            await channel_layer.group_send(
                'admin_orders',
                {
                    'type': 'order_updated',
                    'order': order_data
                }
            )
        
        # Always send updated stats
        await channel_layer.group_send(
            'admin_orders',
            {
                'type': 'order_stats',
                'stats': stats
            }
        )
    
    # Run async function
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(send_notification())
        else:
            loop.run_until_complete(send_notification())
    except Exception as e:
        pass

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    """Signal handler for order status changes"""

    from channels.layers import get_channel_layer
    import asyncio
    
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    # Check if status actually changed
    if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        # Prepare order data
        user_name = instance.user.email
        try:
            if hasattr(instance.user, 'profile') and instance.user.profile.full_name:
                user_name = instance.user.profile.full_name
        except:
            pass
        
        order_data = {
            'id': instance.id,
            'order_number': instance.order_number,
            'user_email': instance.user.email,
            'user_name': user_name,
            'total_amount': float(instance.total_amount),
            'status': instance.status,
            'previous_status': getattr(instance, '_previous_status', None),
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }
        
        # Get updated order stats (ultra-optimized - only pending count for speed)
        pending_count = Order.objects.filter(status='pending').count()
        
        stats = {
            'pending_orders': pending_count,
            'total_orders': Order.objects.count(),  # Only if needed
        }
        
        # Send to admin orders group
        async def send_status_notification():

            await channel_layer.group_send(
                'admin_orders',
                {
                    'type': 'order_status_changed',
                    'order': order_data
                }
            )
            # Always send updated stats
            await channel_layer.group_send(
                'admin_orders',
                {
                    'type': 'order_stats',
                    'stats': stats
                }
            )
        
        # Run async function
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(send_status_notification())
            else:
                loop.run_until_complete(send_status_notification())
        except Exception as e:
            pass

# Override Order.save to track status changes
def track_status_change(sender, instance, **kwargs):
    """Track status changes for order model"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None

# Connect the signal
post_save.connect(track_status_change, sender=Order)
