from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from products.models import Product, ProductImage, ProductVariant
from products.serializers import ProductDetailSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_product(request, slug):
    """
    Get single product details by slug
    Returns: Complete product information with images and variants
    """
    try:
        print(f"🔍 PRODUCT_VIEW: get_single_product called - Slug: {slug}, User: {request.user}, Session: {request.session.session_key}")
        
        # Get product with related data
        product = get_object_or_404(
            Product.objects.select_related('category', 'subcategory')
            .prefetch_related('images', 'variants__dynamic_options'),
            slug=slug,
            status='active'
        )
        print(f"🔍 PRODUCT_VIEW: Product found - ID: {product.id}, Title: {product.title}")
        
        # Check if this is causing cart additions
        print(f"🔍 PRODUCT_VIEW: Stack trace:")
        import traceback
        traceback.print_stack()
        
        # Use ProductDetailSerializer to get all fields including display_price
        serializer = ProductDetailSerializer(product)
        product_data = serializer.data
        
        # Fix image URLs to include full domain
        if product_data.get('images'):
            for image in product_data['images']:
                if image.get('image_url') and image['image_url'].startswith('/'):
                    image['image_url'] = f"http://127.0.0.1:8000{image['image_url']}"
        
        # Add additional fields for backward compatibility
        product_data['primary_image'] = product_data['images'][0] if product_data['images'] else None
        product_data['total_images'] = len(product_data['images'])
        product_data['total_variants'] = len(product_data['variants'])
        
        
        return Response({
            'success': True,
            'product': product_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
