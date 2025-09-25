from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model

from ...models import Conversation, Message, Participant
from ...serializers import (
    ConversationSerializer, 
    ConversationListSerializer,
    ConversationCreateSerializer,
    ConversationUpdateSerializer
)

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations based on user role"""
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            # Staff can see all conversations
            return Conversation.objects.all()
        else:
            # Customers can only see their own conversations
            return Conversation.objects.filter(customer=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ConversationUpdateSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to handle duplicate conversations"""
        user = request.user
        
        # Check if customer already has an open conversation
        existing_conversation = Conversation.objects.filter(
            customer=user,
            status='open'
        ).first()
        
        if existing_conversation:
            # Return existing conversation instead of creating new one
            serializer = self.get_serializer(existing_conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new conversation if none exists
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create conversation and add customer as participant"""
        conversation = serializer.save()
        
        # Add customer as participant
        Participant.objects.get_or_create(
            conversation=conversation,
            user=conversation.customer
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign conversation to staff member"""
        conversation = self.get_object()
        staff_id = request.data.get('staff_id')
        
        if not staff_id:
            return Response(
                {'error': 'staff_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            staff_user = User.objects.get(id=staff_id, is_staff=True)
            conversation.assigned_to = staff_user
            conversation.save()
            
            # Add staff as participant
            Participant.objects.get_or_create(
                conversation=conversation,
                user=staff_user
            )
            
            return Response({'message': 'Conversation assigned successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid staff user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close conversation"""
        conversation = self.get_object()
        conversation.status = 'closed'
        conversation.save()
        
        return Response({'message': 'Conversation closed successfully'})
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen conversation"""
        conversation = self.get_object()
        conversation.status = 'open'
        conversation.save()
        
        return Response({'message': 'Conversation reopened successfully'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark conversation as read"""
        conversation = self.get_object()
        user = request.user
        
        if user.is_staff or user.is_superuser:
            conversation.reset_unread_count(is_staff=True)
        else:
            conversation.reset_unread_count(is_staff=False)
        
        return Response({'message': 'Conversation marked as read'})


class ConversationInboxView(viewsets.ReadOnlyModelViewSet):
    """ViewSet for admin/staff inbox with filtering"""
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations for inbox"""
        user = self.request.user
        
        if not (user.is_staff or user.is_superuser):
            return Conversation.objects.none()
        
        queryset = Conversation.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by assigned staff
        if self.request.query_params.get('assigned_to_me') == 'true':
            queryset = queryset.filter(assigned_to=user)
        
        # Filter by unread
        if self.request.query_params.get('unread') == 'true':
            queryset = queryset.filter(unread_staff_count__gt=0)
        
        # Search by customer name/email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer__full_name__icontains=search) |
                Q(customer__email__icontains=search)
            )
        
        # Remove duplicates by customer - keep only the latest conversation per customer
        from django.db.models import Max
        latest_conversations = queryset.values('customer').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)
        
        queryset = queryset.filter(id__in=latest_conversations)
        
        return queryset.order_by('-last_message_at', '-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get inbox statistics"""
        user = request.user
        
        if not (user.is_staff or user.is_superuser):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        stats = {
            'total_conversations': Conversation.objects.count(),
            'open_conversations': Conversation.objects.filter(status='open').count(),
            'closed_conversations': Conversation.objects.filter(status='closed').count(),
            'unread_conversations': Conversation.objects.filter(unread_staff_count__gt=0).count(),
            'assigned_to_me': Conversation.objects.filter(assigned_to=user).count(),
            'unread_assigned_to_me': Conversation.objects.filter(
                assigned_to=user, 
                unread_staff_count__gt=0
            ).count()
        }
        
        return Response(stats)
