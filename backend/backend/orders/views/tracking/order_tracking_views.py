from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ...models.orders.order import Order
from ...serializers.tracking.order_tracking_serializer import (
    OrderTrackingSerializer,
    OrderTrackingRequestSerializer
)


class OrderTrackingView(generics.RetrieveAPIView):
    """
    API view for tracking orders by order number
    """
    serializer_class = OrderTrackingSerializer
    permission_classes = [AllowAny]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders that can be tracked"""
        return Order.objects.select_related(
            'user', 'delivery_address'
        ).prefetch_related(
            'items__product__images'
        ).all()
    
    def get_object(self):
        """Get order by order number"""
        order_number = self.kwargs.get('order_number')
        try:
            order = get_object_or_404(Order, order_number=order_number)
            return order
        except Order.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        """Handle order tracking request"""
        order_number = kwargs.get('order_number')
        
        if not order_number:
            return Response({
                'success': False,
                'message': 'Order number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find order by order number (case insensitive)
            order = Order.objects.select_related(
                'user', 'delivery_address'
            ).prefetch_related(
                'items__product__images'
            ).get(order_number__iexact=order_number)
            
            serializer = self.get_serializer(order)
            
            return Response({
                'success': True,
                'message': 'Order found successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found. Please check your order number.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error tracking order: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_order_by_number(request):
    """
    Track order by order number (alternative endpoint)
    """
    serializer = OrderTrackingRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Invalid tracking number',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tracking_number = serializer.validated_data['tracking_number']
    
    try:
        # Find order by order number (case insensitive)
        order = Order.objects.select_related(
            'user', 'delivery_address'
        ).prefetch_related(
            'items__product__images'
        ).get(order_number__iexact=tracking_number)
        
        order_serializer = OrderTrackingSerializer(order)
        
        return Response({
            'success': True,
            'message': 'Order found successfully',
            'data': order_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found. Please check your order number.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error tracking order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_status(request, order_number):
    """
    Get order status by order number
    """
    try:
        order = get_object_or_404(Order, order_number__iexact=order_number)
        
        return Response({
            'success': True,
            'data': {
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'status_color': order.get_status_display_color(),
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'estimated_delivery': order.estimated_delivery,
                'delivered_at': order.delivered_at
            }
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error getting order status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_orders(request):
    """
    Search orders by order number (partial match)
    """
    order_number = request.GET.get('q', '').strip()
    
    if not order_number or len(order_number) < 3:
        return Response({
            'success': False,
            'message': 'Please provide at least 3 characters to search'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Search for orders with partial order number match
        orders = Order.objects.filter(
            order_number__icontains=order_number
        ).select_related(
            'user', 'delivery_address'
        ).prefetch_related(
            'items__product__images'
        )[:10]  # Limit to 10 results
        
        serializer = OrderTrackingSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'message': f'Found {orders.count()} orders',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error searching orders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
