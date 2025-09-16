from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from products.models import Product, ProductImage
from products.serializers import ProductListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_products(request):
    """
    Simple API for homepage product display
    Returns: image, category name, product name, price
    """
    try:
        # Get active products with images
        products = Product.objects.filter(
            status='active'
        ).select_related('category').prefetch_related('images').order_by('-created_at')[:12]
        
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
            
            product_data = {
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'price': float(product.price) if product.price else 0.0,
                'old_price': float(product.old_price) if product.old_price else None,
                'category_name': product.category.name if product.category else None,
                'image_url': image_url,
                'image_alt': primary_image.alt_text if primary_image else product.title,
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
