"""
Wishlist Views
==============

This module contains API views for wishlist functionality.
Provides RESTful endpoints for wishlist operations.

APIs:
- add_to_wishlist: Add items to wishlist
- remove_from_wishlist: Remove items from wishlist
- get_wishlist: Get user's wishlist
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from cart.models import Wishlist, WishlistItem
from cart.serializers import (
    WishlistSerializer,
    AddToWishlistSerializer
)
from products.models import Product, ProductVariant

def get_or_create_wishlist(user):
    """
    Get or create wishlist for authenticated user
    ==============================================
    
    Args:
        user: Authenticated user object
        
    Returns:
        Wishlist: User's wishlist
    """
    wishlist, created = Wishlist.objects.get_or_create(
        user=user,
        is_active=True,
        defaults={'is_active': True}
    )
    return wishlist

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only authenticated users can have wishlists
def add_to_wishlist(request):
    """
    Add Item to Wishlist API
    =========================
    
    Adds a product (with optional variant) to the user's wishlist.
    Only available for authenticated users.
    
    Request Body:
    {
        "product_id": 123,
        "variant_id": 456  // optional
    }
    
    Response:
    {
        "success": true,
        "message": "Item added to wishlist successfully",
        "wishlist_item": {...},
        "wishlist": {...}
    }
    """
    try:
        # Validate request data
        serializer = AddToWishlistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        
        # Get product and variant
        product = Product.objects.get(id=product_id)
        variant = None
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
        
        # Get or create wishlist
        wishlist = get_or_create_wishlist(request.user)
        
        # Check if item already exists in wishlist
        existing_item = WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product,
            variant=variant
        ).first()
        
        if existing_item:
            return Response({
                'success': False,
                'error': 'Item already exists in wishlist'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create new wishlist item
            wishlist_item = WishlistItem.objects.create(
                wishlist=wishlist,
                product=product,
                variant=variant
            )
        
        # Serialize response
        wishlist_serializer = WishlistSerializer(wishlist)
        
        return Response({
            'success': True,
            'message': 'Item added to wishlist successfully',
            'wishlist_item': {
                'id': wishlist_item.id,
                'product_title': product.title,
                'variant_title': variant.title if variant else None,
                'current_price': float(wishlist_item.get_current_price()),
                'is_available': wishlist_item.is_available()
            },
            'wishlist': wishlist_serializer.data
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
@permission_classes([IsAuthenticated])  # Only authenticated users
def remove_from_wishlist(request, item_id):
    """
    Remove Item from Wishlist API
    ==============================
    
    Removes a specific item from the user's wishlist.
    
    URL: /api/wishlist/items/{item_id}/remove/
    
    Response:
    {
        "success": true,
        "message": "Item removed from wishlist successfully"
    }
    """
    try:
        # Get wishlist item
        wishlist_item = get_object_or_404(WishlistItem, id=item_id)
        
        # Verify ownership
        if wishlist_item.wishlist.user != request.user:
            return Response({
                'success': False,
                'error': 'Wishlist item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Remove item
        product_title = wishlist_item.product.title
        wishlist_item.delete()
        
        return Response({
            'success': True,
            'message': f'{product_title} removed from wishlist successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only authenticated users
def get_wishlist(request):
    """
    Get Wishlist API
    =================
    
    Retrieves the user's wishlist with all items.
    Includes product details, variants, and availability status.
    
    Response:
    {
        "success": true,
        "wishlist": {...}
    }
    """
    try:
        # Get or create wishlist
        wishlist = get_or_create_wishlist(request.user)
        
        # Clear unavailable items
        unavailable_count = wishlist.clear_unavailable_items()
        
        # Serialize wishlist
        wishlist_serializer = WishlistSerializer(wishlist)
        
        response_data = {
            'success': True,
            'wishlist': wishlist_serializer.data
        }
        
        if unavailable_count > 0:
            response_data['message'] = f'{unavailable_count} unavailable items removed from wishlist'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
