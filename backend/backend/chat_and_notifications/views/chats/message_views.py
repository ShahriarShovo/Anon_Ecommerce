from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model

from ...models import Conversation, Message
from ...serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    MessageListSerializer,
    MessageMarkReadSerializer
)

User = get_user_model()


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages based on user access"""
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation')
        
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                # Check if user has access to this conversation
                if conversation.customer == user or conversation.assigned_to == user:
                    return Message.objects.filter(conversation=conversation)
                elif user.is_staff or user.is_superuser:
                    return Message.objects.filter(conversation=conversation)
            except Conversation.DoesNotExist:
                pass
        
        # Return empty queryset if no valid conversation
        return Message.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MessageListSerializer
        elif self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Create message and set sender"""
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark multiple messages as read"""
        serializer = MessageMarkReadSerializer(data=request.data)
        
        if serializer.is_valid():
            message_ids = serializer.validated_data.get('message_ids', [])
            conversation_id = serializer.validated_data.get('conversation_id')
            user = request.user
            
            if conversation_id:
                # Mark all unread messages in conversation as read
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    if conversation in self.get_user_conversations(user):
                        messages = Message.objects.filter(
                            conversation=conversation,
                            is_read_by_recipient=False
                        )
                        updated_count = 0
                        for message in messages:
                            message.mark_as_read()
                            updated_count += 1
                        
                        # Reset unread count for the conversation
                        print(f"MarkMessagesAsRead - Before reset: unread_user_count={conversation.unread_user_count}, unread_staff_count={conversation.unread_staff_count}")
                        if user.is_staff or user.is_superuser:
                            conversation.reset_unread_count(is_staff=True)
                        else:
                            conversation.reset_unread_count(is_staff=False)
                        print(f"MarkMessagesAsRead - After reset: unread_user_count={conversation.unread_user_count}, unread_staff_count={conversation.unread_staff_count}")
                        
                        return Response({
                            'message': f'{updated_count} messages marked as read in conversation',
                            'updated_count': updated_count
                        })
                except Conversation.DoesNotExist:
                    return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Mark specific messages as read
                messages = Message.objects.filter(
                    id__in=message_ids,
                    conversation__in=self.get_user_conversations(user)
                )
                
                # Mark messages as read
                updated_count = 0
                for message in messages:
                    if not message.is_read_by_recipient:
                        message.mark_as_read()
                        updated_count += 1
                
                return Response({
                    'message': f'{updated_count} messages marked as read',
                    'updated_count': updated_count
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark single message as read"""
        message = self.get_object()
        
        if not message.is_read_by_recipient:
            message.mark_as_read()
            return Response({'message': 'Message marked as read'})
        
        return Response({'message': 'Message already read'})
    
    def get_user_conversations(self, user):
        """Get conversations user has access to"""
        if user.is_staff or user.is_superuser:
            return Conversation.objects.all()
        else:
            return Conversation.objects.filter(
                Q(customer=user) | Q(assigned_to=user)
            )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread message count for user"""
        user = request.user
        conversations = self.get_user_conversations(user)
        
        if user.is_staff or user.is_superuser:
            unread_count = sum(conv.unread_staff_count for conv in conversations)
        else:
            unread_count = sum(conv.unread_user_count for conv in conversations)
        
        # print(f"Unread count API - User: {user.email}, Is staff: {user.is_staff}, Conversations: {len(conversations)}")
        for conv in conversations:
            print(f"Conversation {conv.id}: unread_user_count={conv.unread_user_count}, unread_staff_count={conv.unread_staff_count}")
        # print(f"Total unread count: {unread_count}")
        
        return Response({'unread_count': unread_count})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent messages for user"""
        user = request.user
        limit = int(request.query_params.get('limit', 20))
        
        conversations = self.get_user_conversations(user)
        recent_messages = Message.objects.filter(
            conversation__in=conversations
        ).order_by('-created_at')[:limit]
        
        serializer = MessageListSerializer(recent_messages, many=True)
        return Response(serializer.data)


class MessageMarkReadView(viewsets.GenericViewSet):
    """View for marking messages as read"""
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Mark multiple messages as read"""
        serializer = MessageMarkReadSerializer(data=request.data)
        
        if serializer.is_valid():
            message_ids = serializer.validated_data['message_ids']
            user = request.user
            
            # Get messages that user has access to
            messages = Message.objects.filter(
                id__in=message_ids,
                conversation__in=self.get_user_conversations(user)
            )
            
            # Mark messages as read
            updated_count = 0
            for message in messages:
                if not message.is_read_by_recipient:
                    message.mark_as_read()
                    updated_count += 1
            
            return Response({
                'message': f'{updated_count} messages marked as read',
                'updated_count': updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_user_conversations(self, user):
        """Get conversations user has access to"""
        if user.is_staff or user.is_superuser:
            return Conversation.objects.all()
        else:
            return Conversation.objects.filter(
                Q(customer=user) | Q(assigned_to=user)
            )