from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Logo, Banner
from .serializers import (
    LogoSerializer, LogoCreateSerializer, ActiveLogoSerializer,
    BannerSerializer, BannerCreateSerializer, ActiveBannerSerializer
)

class LogoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing logos
    """
    queryset = Logo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LogoCreateSerializer
        return LogoSerializer
    
    def get_queryset(self):
        """Filter logos based on user permissions"""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Logo.objects.all()
        return Logo.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_active_logo(self, request):
        """Get the currently active logo (public endpoint)"""
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
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a specific logo"""
        logo = self.get_object()
        
        # Deactivate all other logos
        Logo.objects.filter(is_active=True).update(is_active=False)
        
        # Activate this logo
        logo.is_active = True
        logo.save()
        
        serializer = LogoSerializer(logo)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get logo statistics"""
        total_logos = Logo.objects.count()
        active_logos = Logo.objects.filter(is_active=True).count()
        
        return Response({
            'total_logos': total_logos,
            'active_logos': active_logos,
            'inactive_logos': total_logos - active_logos
        })

class BannerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing banners
    """
    queryset = Banner.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BannerCreateSerializer
        return BannerSerializer
    
    def get_queryset(self):
        """Filter banners based on user permissions"""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Banner.objects.all()
        return Banner.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_active_banners(self, request):
        """Get all active banners for public display"""
        try:

            active_banners = Banner.get_active_banners()

            serializer = ActiveBannerSerializer(active_banners, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a specific banner"""
        banner = self.get_object()
        banner.is_active = True
        banner.save()
        
        serializer = BannerSerializer(banner)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a specific banner"""
        banner = self.get_object()
        banner.is_active = False
        banner.save()
        
        serializer = BannerSerializer(banner)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get banner statistics"""
        total_banners = Banner.objects.count()
        active_banners = Banner.objects.filter(is_active=True).count()
        
        return Response({
            'total_banners': total_banners,
            'active_banners': active_banners,
            'inactive_banners': total_banners - active_banners
        })