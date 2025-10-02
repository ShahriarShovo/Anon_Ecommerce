from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ...models.orders.order import Order

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_orders_count(request):
    """
    Get count of pending orders for admin dashboard
    """
    try:
        # Check if user is staff/admin
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'error': 'Access denied. Admin privileges required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Count pending orders
        pending_count = Order.objects.filter(status='pending').count()
        
        return Response({
            'pending_count': pending_count,
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get pending orders count: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_statistics(request):
    """
    Get comprehensive order statistics for admin dashboard
    """
    try:
        # Check if user is staff/admin
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'error': 'Access denied. Admin privileges required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get order statistics
        stats = {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'processing_orders': Order.objects.filter(status='processing').count(),
            'shipped_orders': Order.objects.filter(status='shipped').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
            'refunded_orders': Order.objects.filter(status='refunded').count(),
        }
        
        return Response({
            'statistics': stats,
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get order statistics: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
