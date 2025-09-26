from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from orders.models.orders.order import Order
from orders.models.orders.order_item import OrderItem
from orders.models.orders.address import Address
from orders.models.payments.payment import Payment
from orders.models.payments.payment_method import PaymentMethod
from orders.serializers.orders.order_serializer import OrderSerializer, OrderCreateSerializer
from orders.serializers.orders.address_serializer import AddressCreateSerializer
from cart.models.cart import Cart, CartItem


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Create a new order from cart items
    """
    print(f"🛒 Order Creation: User: {request.user.email}")
    print(f"🛒 Order Creation: Request data: {request.data}")
    
    try:
        with transaction.atomic():
            # Get user's cart (handle multiple carts)
            try:
                # Get the most recent cart if multiple exist
                cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
                if not cart:
                    print(f"🛒 No cart found for user: {request.user.email}")
                    return Response({
                        'success': False,
                        'message': 'No cart found for user'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_items = CartItem.objects.filter(cart=cart)
                print(f"🛒 Cart found: ID {cart.id}, Items: {cart_items.count()}")
                
                # Clean up any duplicate carts (keep only the most recent one)
                duplicate_carts = Cart.objects.filter(user=request.user).exclude(id=cart.id)
                if duplicate_carts.exists():
                    print(f"🛒 Found {duplicate_carts.count()} duplicate carts, cleaning up...")
                    duplicate_carts.delete()
                    print(f"🛒 Cleaned up duplicate carts")
                    
            except Exception as e:
                print(f"🛒 Error getting cart: {str(e)}")
                return Response({
                    'success': False,
                    'message': 'Error accessing cart'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not cart_items.exists():
                print(f"🛒 Cart is empty for user: {request.user.email}")
                return Response({
                    'success': False,
                    'message': 'Cart is empty'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Handle address - use existing or create new
            address_data = request.data.get('address', {})
            print(f"🛒 Address data: {address_data}")
            
            # Check if address_id is provided (for existing address)
            address_id = request.data.get('address_id')
            if address_id:
                try:
                    address = Address.objects.get(id=address_id, user=request.user)
                    print(f"🛒 Using existing address: ID {address.id}")
                except Address.DoesNotExist:
                    print(f"🛒 Address not found: ID {address_id}")
                    return Response({
                        'success': False,
                        'message': 'Address not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Try to find existing address with same details
                try:
                    address = Address.objects.get(
                        user=request.user,
                        full_name=address_data.get('full_name'),
                        phone_number=address_data.get('phone_number'),
                        address_line_1=address_data.get('address_line_1'),
                        city=address_data.get('city'),
                        country=address_data.get('country')
                    )
                    print(f"🛒 Using existing address: ID {address.id}")
                except Address.DoesNotExist:
                    # Create new address
                    address_serializer = AddressCreateSerializer(
                        data=address_data,
                        context={'request': request}
                    )
                    
                    if not address_serializer.is_valid():
                        print(f"🛒 Address validation failed: {address_serializer.errors}")
                        return Response({
                            'success': False,
                            'message': 'Invalid address data',
                            'errors': address_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    address = address_serializer.save()
                    print(f"🛒 Address created: ID {address.id}")
            
            # Get payment method
            payment_method_type = request.data.get('payment_method', 'cash_on_delivery')
            print(f"🛒 Payment method type: {payment_method_type}")
            
            payment_method = PaymentMethod.objects.filter(
                method_type=payment_method_type,
                is_active=True
            ).first()
            
            if not payment_method:
                print(f"🛒 Payment method not found: {payment_method_type}")
                return Response({
                    'success': False,
                    'message': f'Payment method "{payment_method_type}" not found or inactive'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create order
            order_data = {
                'delivery_address': address.id,
                'notes': request.data.get('notes', ''),
                'subtotal': cart.subtotal,
                'shipping_cost': 0.00,  # Free shipping for now
                'tax_amount': 0.00,     # No tax for now
                'total_amount': cart.subtotal
            }
            print(f"🛒 Order data: {order_data}")
            print(f"🛒 Cart subtotal: {cart.subtotal}")
            
            order_serializer = OrderCreateSerializer(
                data=order_data,
                context={'request': request}
            )
            
            if not order_serializer.is_valid():
                print(f"🛒 Order validation failed: {order_serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Invalid order data',
                    'errors': order_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            order = order_serializer.save()
            print(f"🛒 Order created: ID {order.id}, Number {order.order_number}")
            
            # Create order items from cart items
            for cart_item in cart_items:
                print(f"🛒 Creating order item for product: {cart_item.product.title}")
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.get_total_price(),  # Use method instead of attribute
                    product_name=cart_item.product.title,
                    product_sku=getattr(cart_item.product, 'sku', None),  # Handle missing sku field
                    variant_title=str(cart_item.variant) if cart_item.variant else None
                )
                print(f"🛒 Order item created: ID {order_item.id}")
            
            # Create payment
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                status='pending' if payment_method.is_cod else 'processing'
            )
            print(f"🛒 Payment created: ID {payment.id}, Status: {payment.status}")
            
            # Clear cart after successful order
            cart_items.delete()
            
            # Delete the cart model completely after successful order
            cart_id = cart.id
            cart.delete()
            print(f"🛒 Cart deleted completely: ID {cart_id}")
            
            # Return order details
            order_serializer = OrderSerializer(order, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Order placed successfully',
                'order': order_serializer.data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        print(f"🛒 Order creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Failed to create order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderListView(generics.ListAPIView):
    """
    List all orders for the authenticated user
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if specific user ID is requested (for admin viewing user orders)
        user_id = self.request.query_params.get('user')
        
        if user_id and (self.request.user.is_staff or self.request.user.is_superuser):
            # Admin can view specific user's orders
            try:
                from accounts.models import User
                target_user = User.objects.get(id=user_id)
                return Order.objects.filter(user=target_user).order_by('-created_at')
            except User.DoesNotExist:
                return Order.objects.none()
        elif self.request.user.is_staff or self.request.user.is_superuser:
            # Admin can see all orders
            return Order.objects.all().order_by('-created_at')
        else:
            # Regular users can only see their own orders
            return Order.objects.filter(user=self.request.user).order_by('-created_at')


class ActiveOrderListView(generics.ListAPIView):
    """
    List active orders (pending, confirmed, processing, shipped) for the authenticated user
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed', 'processing', 'shipped']
        ).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific order
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class DeliveredOrderListView(generics.ListAPIView):
    """
    List all delivered orders for the authenticated user
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status='delivered'
        ).order_by('-delivered_at', '-created_at')


class CancelledRefundedOrderListView(generics.ListAPIView):
    """
    List all cancelled and refunded orders for the authenticated user
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status__in=['cancelled', 'refunded']
        ).order_by('-updated_at', '-created_at')


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, order_id):
    """
    Update order status (for admin use or order management)
    """
    try:
        # Check if user is admin or staff
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'success': False,
                'message': 'Only admin users can update order status'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Admin can update any order, not just their own
        order = get_object_or_404(Order, id=order_id)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({
                'success': False,
                'message': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order.status = new_status
        
        # If marking as delivered, set delivered_at timestamp
        if new_status == 'delivered' and not order.delivered_at:
            from django.utils import timezone
            order.delivered_at = timezone.now()
        
        order.save()
        
        serializer = OrderSerializer(order, context={'request': request})
        
        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update order status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    """
    Allow customers to cancel their own pending orders
    """
    try:
        # Get the order and ensure it belongs to the current user
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is in pending status
        if order.status != 'pending':
            return Response({
                'success': False,
                'message': f'Order can only be cancelled when status is pending. Current status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cancel reason from request
        cancel_reason = request.data.get('cancel_reason', 'Cancelled by customer')
        
        # Update order status to cancelled
        order.status = 'cancelled'
        order.save()
        
        # You can also store the cancel reason in a separate model if needed
        # For now, we'll just update the status
        
        serializer = OrderSerializer(order, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Order cancelled successfully',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to cancel order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
