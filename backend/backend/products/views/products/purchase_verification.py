from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from products.models import Product
from orders.models import Order, OrderItem


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_purchase_eligibility(request, slug):
    """
    Check if the authenticated user has purchased this product
    Returns: Purchase eligibility status and order information
    """
    try:
        # Get product
        product = get_object_or_404(Product, slug=slug, status='active')
        user = request.user
        
        # Check if user has purchased this product
        # Look for completed orders (delivered status) that contain this product
        purchased_orders = Order.objects.filter(
            user=user,
            status='delivered'  # Only delivered orders count
        ).prefetch_related('items')
        
        # Check if any order item contains this product
        has_purchased = False
        purchase_info = None
        
        for order in purchased_orders:
            order_items = order.items.filter(product=product)
            if order_items.exists():
                has_purchased = True
                # Get the most recent purchase info
                latest_item = order_items.order_by('-created_at').first()
                purchase_info = {
                    'order_number': order.order_number,
                    'purchase_date': order.delivered_at.isoformat() if order.delivered_at else order.created_at.isoformat(),
                    'product_name': latest_item.product_name,
                    'variant_title': latest_item.variant_title,
                    'quantity': latest_item.quantity,
                    'unit_price': float(latest_item.unit_price),
                    'total_price': float(latest_item.total_price)
                }
                break
        
        # Check if user has already reviewed this product
        from products.models import ProductReview
        existing_review = ProductReview.objects.filter(
            product=product,
            user=user
        ).first()
        
        has_reviewed = existing_review is not None
        review_info = None
        
        if has_reviewed:
            review_info = {
                'id': existing_review.id,
                'rating': existing_review.rating,
                'title': existing_review.title,
                'comment': existing_review.comment,
                'created_at': existing_review.created_at.isoformat(),
                'is_approved': existing_review.is_approved
            }
        
        return Response({
            'success': True,
            'has_purchased': has_purchased,
            'has_reviewed': has_reviewed,
            'can_review': has_purchased and not has_reviewed,
            'purchase_info': purchase_info,
            'review_info': review_info,
            'message': 'Purchase eligibility checked successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error checking purchase eligibility: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_purchase_history(request, slug):
    """
    Get user's purchase history for a specific product
    Returns: List of orders containing this product
    """
    try:
        # Get product
        product = get_object_or_404(Product, slug=slug, status='active')
        user = request.user
        
        # Get all orders containing this product
        orders_with_product = Order.objects.filter(
            user=user,
            items__product=product
        ).distinct().order_by('-created_at')
        
        purchase_history = []
        for order in orders_with_product:
            # Get the specific order items for this product
            order_items = order.items.filter(product=product)
            
            for item in order_items:
                purchase_history.append({
                    'order_number': order.order_number,
                    'order_status': order.status,
                    'purchase_date': order.created_at.isoformat(),
                    'delivered_date': order.delivered_at.isoformat() if order.delivered_at else None,
                    'product_name': item.product_name,
                    'variant_title': item.variant_title,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price),
                    'can_review': order.status == 'delivered'  # Only delivered orders can be reviewed
                })
        
        return Response({
            'success': True,
            'purchase_history': purchase_history,
            'total_purchases': len(purchase_history),
            'delivered_purchases': len([p for p in purchase_history if p['can_review']])
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error fetching purchase history: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
