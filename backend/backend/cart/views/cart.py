"""
Cart Views
==========

This module contains API views for cart functionality.
Provides RESTful endpoints for cart operations.

APIs:
- add_to_cart: Add items to cart
- increase_cart_item_quantity: Increase item quantity
- decrease_cart_item_quantity: Decrease item quantity
- remove_cart_item: Remove an item from the cart
- get_cart: Get user's cart
- clear_cart: Clear all items from cart
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from cart.models import Cart, CartItem
from cart.serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)
from products.models import Product, ProductVariant


def get_or_create_cart(request):
    """
    Get or create cart for user/session
    ====================================
    
    Returns the appropriate cart based on authentication status:
    - Authenticated users: Get/create user cart
    - Guest users: Get/create session-based cart
    
    Args:
        request: Django request object
        
    Returns:
        Cart: User's or session's cart
    """
    if request.user.is_authenticated:
        # Authenticated user - get or create user cart
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'is_active': True}
        )
    else:
        # Guest user - get or create session cart
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Debug: Log session key
        print(f"🛒 Backend: Session key: {session_key}")
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            is_active=True,
            defaults={'is_active': True}
        )
        
        # Debug: Log cart creation
        if created:
            print(f"🛒 Backend: Created new cart with session key: {session_key}")
        else:
            print(f"🛒 Backend: Found existing cart with session key: {session_key}")
    
    return cart


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def add_to_cart(request):
    """
    Add Item to Cart API
    ====================
    
    Adds a product (with optional variant) to the user's cart.
    Supports both authenticated users and guest users.
    
    Request Body:
    {
        "product_id": 123,
        "quantity": 2,
        "variant_id": 456  // optional
    }
    
    Response:
    {
        "success": true,
        "message": "Item added to cart successfully",
        "cart_item": {...},
        "cart": {...}
    }
    """
    try:
        # Validate request data
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        variant_id = serializer.validated_data.get('variant_id')
        
        # Get product and variant
        product = Product.objects.get(id=product_id)
        variant = None
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
        
        # Get or create cart
        cart = get_or_create_cart(request)
        
        # Debug: Log cart details
        print(f"🛒 Backend: Add to cart - Cart ID: {cart.id}, Session Key: {cart.session_key}, User: {cart.user}")
        
        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()
        
        with transaction.atomic():
            if existing_item:
                # Update existing item quantity
                if existing_item.can_increase_quantity(quantity):
                    existing_item.quantity += quantity
                    existing_item.save()
                    cart_item = existing_item
                else:
                    return Response({
                        'success': False,
                        'error': 'Not enough items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new cart item
                unit_price = variant.price if variant else product.price
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    unit_price=unit_price
                )
            
            # Update cart totals
            cart.calculate_totals()
        
        # Serialize response
        cart_serializer = CartSerializer(cart)
        
        return Response({
            'success': True,
            'message': 'Item added to cart successfully',
            'cart_item': {
                'id': cart_item.id,
                'product_title': product.title,
                'variant_title': variant.title if variant else None,
                'quantity': cart_item.quantity,
                'unit_price': float(cart_item.unit_price),
                'total_price': float(cart_item.get_total_price())
            },
            'cart': cart_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ProductVariant.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product variant not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def remove_cart_item(request, item_id):
    """
    Remove Cart Item API
    ====================
    
    Removes a specific item from the user's cart.
    
    URL: /api/cart/items/{item_id}/remove/
    
    Response:
    {
        "success": true,
        "message": "Item removed successfully",
        "cart": {...}
    }
    """
    try:
        print(f"🛒 Backend: Remove cart item - Item ID: {item_id}")
        
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id)
        print(f"🛒 Backend: Found cart item: {cart_item.id}, Product: {cart_item.product.title}")
        
        # Verify cart ownership
        cart = get_or_create_cart(request)
        print(f"🛒 Backend: Cart ID: {cart.id}, Session Key: {cart.session_key}, User: {cart.user}")
        
        if cart_item.cart != cart:
            print(f"🛒 Backend: Cart ownership mismatch - Item cart: {cart_item.cart.id}, User cart: {cart.id}")
            return Response({
                'success': False,
                'error': 'Cart item not found in your cart'
            }, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            # Delete the item
            print(f"🛒 Backend: Deleting cart item: {cart_item.id}")
            cart_item.delete()
            
            # Update cart totals
            cart.calculate_totals()
            print(f"🛒 Backend: Cart totals updated - Total items: {cart.total_items}, Subtotal: {cart.subtotal}")
        
        # Serialize response
        cart_serializer = CartSerializer(cart)
        
        print(f"🛒 Backend: Remove successful - Returning cart with {len(cart_serializer.data.get('items', []))} items")
        
        return Response({
            'success': True,
            'message': 'Item removed successfully',
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"🛒 Backend: Remove cart item error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def increase_cart_item_quantity(request, item_id):
    """
    Increase Cart Item Quantity API
    ================================
    
    Increases the quantity of a specific cart item by 1.
    Validates stock availability before increasing.
    
    URL: /api/cart/items/{item_id}/increase/
    
    Response:
    {
        "success": true,
        "message": "Quantity increased successfully",
        "cart_item": {...},
        "cart": {...}
    }
    """
    try:
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verify cart ownership
        cart = get_or_create_cart(request)
        if cart_item.cart != cart:
            return Response({
                'success': False,
                'error': 'Cart item not found in your cart'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if quantity can be increased
        if not cart_item.can_increase_quantity(1):
            return Response({
                'success': False,
                'error': 'Not enough items available in stock'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Increase quantity
            cart_item.increase_quantity(1)
            
            # Update cart totals
            cart.calculate_totals()
        
        # Serialize response
        cart_serializer = CartSerializer(cart)
        
        return Response({
            'success': True,
            'message': 'Quantity increased successfully',
            'cart_item': {
                'id': cart_item.id,
                'product_title': cart_item.product.title,
                'variant_title': cart_item.variant.title if cart_item.variant else None,
                'quantity': cart_item.quantity,
                'unit_price': float(cart_item.unit_price),
                'total_price': float(cart_item.get_total_price())
            },
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def decrease_cart_item_quantity(request, item_id):
    """
    Decrease Cart Item Quantity API
    ================================
    
    Decreases the quantity of a specific cart item by 1.
    Removes the item if quantity becomes 0.
    
    URL: /api/cart/items/{item_id}/decrease/
    
    Response:
    {
        "success": true,
        "message": "Quantity decreased successfully",
        "cart_item": {...} or null if removed,
        "cart": {...}
    }
    """
    try:
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verify cart ownership
        cart = get_or_create_cart(request)
        if cart_item.cart != cart:
            return Response({
                'success': False,
                'error': 'Cart item not found in your cart'
            }, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            # Decrease quantity (removes item if quantity becomes 0)
            item_removed = not cart_item.decrease_quantity(1)
            
            # Update cart totals
            cart.calculate_totals()
        
        # Serialize response
        cart_serializer = CartSerializer(cart)
        
        response_data = {
            'success': True,
            'message': 'Item removed from cart' if item_removed else 'Quantity decreased successfully',
            'cart': cart_serializer.data
        }
        
        if not item_removed:
            response_data['cart_item'] = {
                'id': cart_item.id,
                'product_title': cart_item.product.title,
                'variant_title': cart_item.variant.title if cart_item.variant else None,
                'quantity': cart_item.quantity,
                'unit_price': float(cart_item.unit_price),
                'total_price': float(cart_item.get_total_price())
            }
        else:
            response_data['cart_item'] = None
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def get_cart(request):
    """
    Get Cart API
    =============
    
    Retrieves the user's current cart with all items.
    Includes product details, variants, and calculated totals.
    
    Response:
    {
        "success": true,
        "cart": {...}
    }
    """
    try:
        # Get or create cart
        cart = get_or_create_cart(request)
        
        # Debug: Log cart details
        print(f"🛒 Backend: Get cart - Cart ID: {cart.id}, Session Key: {cart.session_key}, User: {cart.user}")
        print(f"🛒 Backend: Get cart - Items count: {cart.items.count()}")
        
        # Clear expired items
        expired_count = cart.clear_expired_items()
        
        # Serialize cart
        cart_serializer = CartSerializer(cart)
        
        response_data = {
            'success': True,
            'cart': cart_serializer.data
        }
        
        if expired_count > 0:
            response_data['message'] = f'{expired_count} expired items removed from cart'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def clear_cart(request):
    """
    Clear Cart API
    ===============
    
    Removes all items from the user's cart.
    
    Response:
    {
        "success": true,
        "message": "Cart cleared successfully"
    }
    """
    try:
        # Get cart
        cart = get_or_create_cart(request)
        
        # Clear all items
        items_count = cart.items.count()
        cart.items.all().delete()
        
        # Reset cart totals
        cart.total_items = 0
        cart.subtotal = 0.00
        cart.save(update_fields=['total_items', 'subtotal', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Cart cleared successfully. {items_count} items removed.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
