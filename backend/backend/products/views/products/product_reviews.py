from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count

from products.models import Product, ProductReview


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_reviews(request, slug):
    """
    Get product reviews by product slug
    Returns: Reviews with ratings and user information
    """
    try:
        # Get product
        product = get_object_or_404(Product, slug=slug, status='active')
        
        # Get reviews for this product
        reviews = ProductReview.objects.filter(
            product=product,
            is_approved=True
        ).select_related('user').order_by('-created_at')
        
        # Calculate average rating
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        total_reviews = reviews.count()
        
        # Rating distribution
        rating_distribution = reviews.values('rating').annotate(count=Count('rating')).order_by('-rating')
        
        # Prepare reviews data
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user_name': review.user.full_name if review.user and review.user.full_name else 'Anonymous',
                'user_avatar': None,  # You can add avatar field later
                'rating': review.rating,
                'title': review.title,
                'comment': review.comment,
                'created_at': review.created_at.isoformat(),
                'is_verified_purchase': review.is_verified_purchase,
                'helpful_count': review.helpful_count,
            })
        
        return Response({
            'success': True,
            'product_slug': product.slug,
            'product_title': product.title,
            'average_rating': round(avg_rating, 1),
            'total_reviews': total_reviews,
            'rating_distribution': list(rating_distribution),
            'reviews': reviews_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # You can add authentication later
def create_product_review(request, slug):
    """
    Create a new product review
    """
    try:
        # Get product
        product = get_object_or_404(Product, slug=slug, status='active')
        
        # Get review data
        rating = request.data.get('rating')
        title = request.data.get('title', '')
        comment = request.data.get('comment', '')
        user_name = request.data.get('user_name', 'Anonymous')
        user_email = request.data.get('user_email', '')
        
        # Validate rating
        if not rating or not (1 <= int(rating) <= 5):
            return Response({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create review
        review = ProductReview.objects.create(
            product=product,
            rating=int(rating),
            title=title,
            comment=comment,
            user_name=user_name,
            user_email=user_email,
            is_approved=True  # Auto-approve for now
        )
        
        return Response({
            'success': True,
            'message': 'Review submitted successfully',
            'review_id': review.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
