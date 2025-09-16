from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from products.models import Product, ProductImage, ProductReview
from products.serializers import ProductListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_products(request):
    """
    Simple API for homepage product display
    Returns: image, category name, product name, price
    """
    try:
        # Get active products with images and reviews
        products = Product.objects.filter(
            status='active'
        ).select_related('category').prefetch_related('images', 'reviews').order_by('-created_at')[:12]
        
        # Prepare response data
        products_data = []
        for product in products:
            # Get primary image
            primary_image = product.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = product.images.first()
            
            # Build full image URL
            image_url = None
            if primary_image and primary_image.image_url:
                # Make sure we have a full URL
                if primary_image.image_url.startswith('http'):
                    image_url = primary_image.image_url
                else:
                    # Add domain for relative URLs
                    image_url = f"http://127.0.0.1:8000{primary_image.image_url}"
            
            # Calculate average rating from reviews
            approved_reviews = product.reviews.filter(is_approved=True)
            average_rating = 0.0
            review_count = 0
            
            if approved_reviews.exists():
                total_rating = sum(review.rating for review in approved_reviews)
                review_count = approved_reviews.count()
                average_rating = round(total_rating / review_count, 1)
            
            product_data = {
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'price': float(product.price) if product.price else 0.0,
                'old_price': float(product.old_price) if product.old_price else None,
                'category_name': product.category.name if product.category else None,
                'image_url': image_url,
                'image_alt': primary_image.alt_text if primary_image else product.title,
                'average_rating': average_rating,
                'review_count': review_count,
            }
            products_data.append(product_data)
        
        return Response({
            'success': True,
            'products': products_data,
            'count': len(products_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
