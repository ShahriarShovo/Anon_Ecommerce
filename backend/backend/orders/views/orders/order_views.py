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
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                print(f"🛒 Cart found: ID {cart.id}, Items: {cart_items.count()}")
            except Cart.DoesNotExist:
                print(f"🛒 No cart found for user: {request.user.email}")
                return Response({
                    'success': False,
                    'message': 'No cart found for user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not cart_items.exists():
                print(f"🛒 Cart is empty for user: {request.user.email}")
                return Response({
                    'success': False,
                    'message': 'Cart is empty'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create address from request data
            address_data = request.data.get('address', {})
            print(f"🛒 Address data: {address_data}")
            
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
            cart.subtotal = 0.00
            cart.total_items = 0
            cart.save()
            print(f"🛒 Cart cleared: ID {cart.id}")
            
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
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific order
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
