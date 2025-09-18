"""
Clear Cart API
==============

This module contains API views for clearing cart functionality.
Provides a dedicated endpoint for clearing all items from cart.

API:
- clear_cart: Clear all items from user's cart
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from cart.models import Cart
from cart.serializers import CartSerializer


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
        print(f"🛒 Backend: Clear Cart - Session key: {session_key}")
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            is_active=True,
            defaults={'is_active': True}
        )
        
        # Debug: Log cart creation
        if created:
            print(f"🛒 Backend: Clear Cart - Created new cart with session key: {session_key}")
        else:
            print(f"🛒 Backend: Clear Cart - Found existing cart with session key: {session_key}")
    
    return cart


@api_view(['DELETE'])
@permission_classes([AllowAny])  # Allow both authenticated and guest users
def clear_cart(request):
    """
    Clear Cart API
    ===============
    
    Removes all items from the user's cart.
    Supports both authenticated users and guest users.
    
    URL: /api/cart/clear/
    
    Response:
    {
        "success": true,
        "message": "Cart cleared successfully",
        "cart": {...}
    }
    """
    try:
        print(f"🛒 Backend: Clear Cart - Starting clear operation")
        
        # Get cart
        cart = get_or_create_cart(request)
        print(f"🛒 Backend: Clear Cart - Cart ID: {cart.id}, Session Key: {cart.session_key}, User: {cart.user}")
        
        # Count items before clearing
        items_count = cart.items.count()
        print(f"🛒 Backend: Clear Cart - Items to clear: {items_count}")
        
        with transaction.atomic():
            # Clear all items
            cart.items.all().delete()
            print(f"🛒 Backend: Clear Cart - Deleted {items_count} items")
            
            # Reset cart totals
            cart.total_items = 0
            cart.subtotal = 0.00
            cart.save(update_fields=['total_items', 'subtotal', 'updated_at'])
            print(f"🛒 Backend: Clear Cart - Reset cart totals")
        
        # Serialize response
        cart_serializer = CartSerializer(cart)
        
        print(f"🛒 Backend: Clear Cart - Successfully cleared cart with {len(cart_serializer.data.get('items', []))} items")
        
        return Response({
            'success': True,
            'message': f'Cart cleared successfully. {items_count} items removed.',
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"🛒 Backend: Clear Cart - Error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
