from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from ...models.notifications.discount import Discount, DiscountUsage
from ...serializers.notifications.discount import (
    DiscountSerializer,
    DiscountCreateSerializer,
    DiscountUsageSerializer,
    DiscountCalculationSerializer,
    DiscountStatsSerializer
)

User = get_user_model()


class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing discounts"""
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Discount.objects.all()
        return Discount.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DiscountCreateSerializer
        return DiscountSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_discounts(self, request):
        """Get active discounts for public display"""
        now = timezone.now()
        discounts = Discount.objects.filter(
            status='active',
            valid_from__lte=now,
            show_in_notifications=True
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=now)
        ).filter(
            Q(usage_limit__isnull=True) | Q(usage_count__lt=F('usage_limit'))
        ).order_by('-percentage', '-created_at')
        
        serializer = self.get_serializer(discounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def calculate_discount(self, request):
        """Calculate discount for cart items"""
        serializer = DiscountCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart_items = serializer.validated_data['cart_items']
        user_id = serializer.validated_data.get('user_id')
        session_key = serializer.validated_data.get('session_key', request.session.session_key)
        
        # Get all active discounts
        now = timezone.now()
        discounts = Discount.objects.filter(
            status='active',
            valid_from__lte=now
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=now)
        ).order_by('-percentage')
        
        applicable_discounts = []
        
        for discount in discounts:
            # Check if discount can be applied
            can_apply, message = discount.can_apply_to_cart(cart_items, user_id)
            if can_apply:
                discount_amount = discount.calculate_discount_amount(cart_items)
                if discount_amount > 0:
                    applicable_discounts.append({
                        'discount': DiscountSerializer(discount).data,
                        'discount_amount': discount_amount,
                        'message': message
                    })
        
        # Return the best discount (highest amount)
        if applicable_discounts:
            best_discount = max(applicable_discounts, key=lambda x: x['discount_amount'])
            return Response({
                'applicable_discounts': applicable_discounts,
                'best_discount': best_discount,
                'total_discount_amount': best_discount['discount_amount']
            })
        
        return Response({
            'applicable_discounts': [],
            'best_discount': None,
            'total_discount_amount': 0
        })
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def apply_discount(self, request, pk=None):
        """Apply a specific discount"""
        try:
            discount = self.get_object()
        except Discount.DoesNotExist:
            return Response({'error': 'Discount not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get cart data from request
        cart_items = request.data.get('cart_items', [])
        user_id = request.data.get('user_id')
        session_key = request.session.session_key or request.data.get('session_key')
        
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Check if discount can be applied
        can_apply, message = discount.can_apply_to_cart(cart_items, user_id)
        if not can_apply:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount amount
        discount_amount = discount.calculate_discount_amount(cart_items)
        if discount_amount <= 0:
            return Response({'error': 'No discount applicable'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create discount usage record
        user = User.objects.get(id=user_id) if user_id else None
        
        usage, created = DiscountUsage.objects.get_or_create(
            discount=discount,
            session_key=session_key,
            defaults={
                'user': user,
                'discount_amount': discount_amount,
                'ip_address': self.get_client_ip(request)
            }
        )
        
        if created:
            # Increment discount usage count
            discount.increment_usage()
        
        return Response({
            'success': True,
            'discount_amount': discount_amount,
            'discount_name': discount.name,
            'message': f'Discount applied: {discount.name}'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get discount statistics for admin"""
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        total_discounts = Discount.objects.count()
        active_discounts = Discount.objects.filter(status='active').count()
        
        total_usage = DiscountUsage.objects.count()
        total_discount_amount = DiscountUsage.objects.aggregate(
            total=Sum('discount_amount')
        )['total'] or 0
        
        discounts_by_type = dict(
            Discount.objects.values('discount_type').annotate(
                count=Count('id')
            ).values_list('discount_type', 'count')
        )
        
        recent_discounts = Discount.objects.order_by('-created_at')[:5]
        
        stats_data = {
            'total_discounts': total_discounts,
            'active_discounts': active_discounts,
            'total_usage': total_usage,
            'total_discount_amount': total_discount_amount,
            'discounts_by_type': discounts_by_type,
            'recent_discounts': DiscountSerializer(recent_discounts, many=True).data
        }
        
        serializer = DiscountStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle discount active status"""
        try:
            discount = self.get_object()
            if discount.status == 'active':
                discount.status = 'inactive'
            else:
                discount.status = 'active'
            discount.save(update_fields=['status'])
            
            return Response({
                'status': 'success',
                'status': discount.status
            })
        except Discount.DoesNotExist:
            return Response({'error': 'Discount not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_active_discounts_for_display(self, request):
        """Get active discounts that should be displayed in notifications"""
        now = timezone.now()
        print(f"Discount API: Getting active discounts for display at {now}")
        
        # Get all discounts first
        all_discounts = Discount.objects.all()
        print(f"Discount API: Total discounts in database: {all_discounts.count()}")
        
        # Debug: Check each discount
        for discount in all_discounts:
            print(f"Discount API: - {discount.name} (status: {discount.status}, show_in_notifications: {discount.show_in_notifications}, valid_from: {discount.valid_from})")
        
        # Filter active discounts
        discounts = Discount.objects.filter(
            status='active',
            valid_from__lte=now,
            show_in_notifications=True
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=now)
        ).order_by('-percentage', '-created_at')
        
        print(f"Discount API: Active discounts found: {discounts.count()}")
        for discount in discounts:
            print(f"Discount API: - {discount.name} (status: {discount.status}, show_in_notifications: {discount.show_in_notifications})")
        
        # Convert to notification format
        notifications = []
        for discount in discounts:
            notifications.append({
                'id': f'discount_{discount.id}',
                'title': f'🎉 {discount.name}',
                'message': discount.notification_message or f'Get {discount.percentage}% off on your purchase!',
                'notification_type': 'promotion',
                'target_type': 'all',
                'is_active': True,
                'priority': discount.percentage,
                'created_at': discount.created_at,
                'discount_id': discount.id
            })
        
        print(f"Discount API: Returning {len(notifications)} notifications")
        return Response(notifications)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DiscountUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing discount usage"""
    serializer_class = DiscountUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return DiscountUsage.objects.all()
        return DiscountUsage.objects.filter(user=user)
