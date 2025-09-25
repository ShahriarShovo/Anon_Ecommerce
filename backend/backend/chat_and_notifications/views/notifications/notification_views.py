from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from ...models.notifications.notification import Notification, NotificationView
from ...serializers.notifications.notification import (
    NotificationSerializer, 
    NotificationCreateSerializer,
    NotificationViewSerializer,
    NotificationStatsSerializer
)

User = get_user_model()


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_notifications(self, request):
        """Get active notifications for visitors (public endpoint)"""
        notifications = Notification.objects.filter(
            is_active=True,
            target_type__in=['all', 'users']
        ).filter(
            Q(show_until__isnull=True) | Q(show_until__gt=timezone.now())
        ).order_by('-priority', '-created_at')
        
        # Filter for user-specific notifications if user is authenticated
        if request.user.is_authenticated:
            user_notifications = Notification.objects.filter(
                is_active=True,
                target_type='specific',
                target_users=request.user
            ).filter(
                Q(show_until__isnull=True) | Q(show_until__gt=timezone.now())
            ).order_by('-priority', '-created_at')
            
            notifications = (notifications | user_notifications).distinct()
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def mark_viewed(self, request, pk=None):
        """Mark a notification as viewed by a visitor"""
        try:
            notification = self.get_object()
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Check if already viewed by this session
        view, created = NotificationView.objects.get_or_create(
            notification=notification,
            session_key=session_key,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'ip_address': self.get_client_ip(request)
            }
        )
        
        if created:
            # Update notification view counts
            notification.total_views += 1
            notification.unique_views = NotificationView.objects.filter(
                notification=notification
            ).values('session_key').distinct().count()
            notification.save(update_fields=['total_views', 'unique_views'])
        
        return Response({'status': 'success', 'viewed': created})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics for admin"""
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        total_notifications = Notification.objects.count()
        active_notifications = Notification.objects.filter(is_active=True).count()
        
        total_views = NotificationView.objects.count()
        unique_views = NotificationView.objects.values('session_key').distinct().count()
        
        notifications_by_type = dict(
            Notification.objects.values('notification_type').annotate(
                count=Count('id')
            ).values_list('notification_type', 'count')
        )
        
        recent_notifications = Notification.objects.order_by('-created_at')[:5]
        
        stats_data = {
            'total_notifications': total_notifications,
            'active_notifications': active_notifications,
            'total_views': total_views,
            'unique_views': unique_views,
            'notifications_by_type': notifications_by_type,
            'recent_notifications': NotificationSerializer(recent_notifications, many=True).data
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle notification active status"""
        try:
            notification = self.get_object()
            notification.is_active = not notification.is_active
            notification.save(update_fields=['is_active'])
            
            return Response({
                'status': 'success',
                'is_active': notification.is_active
            })
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NotificationPublicView:
    """Public view for notification display"""
    
    @staticmethod
    def get_active_notifications(request):
        """Get active notifications for public display"""
        notifications = Notification.objects.filter(
            is_active=True,
            target_type__in=['all', 'users']
        ).filter(
            Q(show_until__isnull=True) | Q(show_until__gt=timezone.now())
        ).order_by('-priority', '-created_at')
        
        # Filter for user-specific notifications if user is authenticated
        if request.user.is_authenticated:
            user_notifications = Notification.objects.filter(
                is_active=True,
                target_type='specific',
                target_users=request.user
            ).filter(
                Q(show_until__isnull=True) | Q(show_until__gt=timezone.now())
            ).order_by('-priority', '-created_at')
            
            notifications = (notifications | user_notifications).distinct()
        
        return notifications
