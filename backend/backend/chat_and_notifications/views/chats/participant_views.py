from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from ...models import Conversation, Participant
from ...serializers import (
    ParticipantSerializer,
    ParticipantCreateSerializer,
    ParticipantUpdateSerializer,
    OnlineStatusSerializer
)

User = get_user_model()


class ParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversation participants"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter participants based on user access"""
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation')
        
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                # Check if user has access to this conversation
                if conversation.customer == user or conversation.assigned_to == user:
                    return Participant.objects.filter(conversation=conversation)
                elif user.is_staff or user.is_superuser:
                    return Participant.objects.filter(conversation=conversation)
            except Conversation.DoesNotExist:
                pass
        
        # Return empty queryset if no valid conversation
        return Participant.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ParticipantCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ParticipantUpdateSerializer
        return ParticipantSerializer
    
    def perform_create(self, serializer):
        """Create participant"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def update_online_status(self, request, pk=None):
        """Update participant online status"""
        participant = self.get_object()
        serializer = OnlineStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            participant.set_online_status(serializer.validated_data['is_online'])
            return Response({'message': 'Online status updated'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate participant"""
        participant = self.get_object()
        participant.deactivate()
        
        return Response({'message': 'Participant deactivated'})
    
    @action(detail=False, methods=['get'])
    def online_users(self, request):
        """Get online users"""
        user = self.request.user
        
        if not (user.is_staff or user.is_superuser):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        online_participants = Participant.objects.filter(
            is_online=True,
            is_active=True
        ).select_related('user')
        
        serializer = ParticipantSerializer(online_participants, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def set_my_status(self, request):
        """Set current user's online status"""
        user = request.user
        is_online = request.data.get('is_online', False)
        
        # Update all participant records for this user
        participants = Participant.objects.filter(user=user, is_active=True)
        
        for participant in participants:
            participant.set_online_status(is_online)
        
        return Response({
            'message': f'Online status set to {is_online}',
            'is_online': is_online
        })


class OnlineStatusView(viewsets.GenericViewSet):
    """View for managing online status"""
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Set current user's online status"""
        user = request.user
        is_online = request.data.get('is_online', False)
        
        # Update all participant records for this user
        participants = Participant.objects.filter(user=user, is_active=True)
        
        for participant in participants:
            participant.set_online_status(is_online)
        
        return Response({
            'message': f'Online status set to {is_online}',
            'is_online': is_online
        })
    
    def list(self, request):
        """Get online users"""
        user = self.request.user
        
        if not (user.is_staff or user.is_superuser):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        online_participants = Participant.objects.filter(
            is_online=True,
            is_active=True
        ).select_related('user')
        
        serializer = ParticipantSerializer(online_participants, many=True)
        return Response(serializer.data)