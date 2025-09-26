from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from ..models.notifications.logo import Logo
from ..serializers.notifications.logo import (
    LogoSerializer, LogoCreateSerializer, ActiveLogoSerializer
)


class LogoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing site logos
    """
    queryset = Logo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LogoCreateSerializer
        return LogoSerializer
    
    def get_queryset(self):
        """Only show logos to authenticated users"""
        return Logo.objects.all().order_by('-created_at')
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_active_logo(self, request):
        """
        Get the currently active logo (public endpoint)
        """
        try:
            active_logo = Logo.objects.filter(is_active=True).first()
            if active_logo:
                serializer = ActiveLogoSerializer(active_logo)
                return Response(serializer.data)
            else:
                return Response({
                    'message': 'No active logo found',
                    'logo_url': None
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_active(self, request, pk=None):
        """
        Set a logo as active (deactivates all others)
        """
        try:
            logo = self.get_object()
            
            # Deactivate all other logos
            Logo.objects.filter(is_active=True).update(is_active=False)
            
            # Activate this logo
            logo.is_active = True
            logo.save()
            
            serializer = LogoSerializer(logo)
            return Response({
                'message': 'Logo activated successfully',
                'logo': serializer.data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """
        When creating a new logo, deactivate all existing active logos
        """
        # Deactivate all existing active logos
        Logo.objects.filter(is_active=True).update(is_active=False)
        
        # Create new logo
        serializer.save()
    
    def perform_update(self, serializer):
        """
        When updating a logo to active, deactivate all others
        """
        if serializer.validated_data.get('is_active', False):
            Logo.objects.filter(is_active=True).exclude(id=self.get_object().id).update(is_active=False)
        
        serializer.save()
