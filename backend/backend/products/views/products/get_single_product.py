from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from products.models import Product, ProductImage, ProductVariant


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_product(request, slug):
    """
    Get single product details by slug
    Returns: Complete product information with images and variants
    """
    try:
        # Get product with related data
        product = get_object_or_404(
            Product.objects.select_related('category', 'subcategory')
            .prefetch_related('images', 'variants__dynamic_options'),
            slug=slug,
            status='active'
        )
        
        # Get all product images
        images = product.images.all().order_by('position', 'id')
        image_list = []
        for img in images:
            image_list.append({
                'id': img.id,
                'image_url': f"http://127.0.0.1:8000{img.image_url}" if img.image_url else None,
                'alt_text': img.alt_text or product.title,
                'caption': img.caption,
                'position': img.position,
                'is_primary': img.is_primary
            })
        
        # Get product variants
        variants = product.variants.all().order_by('position', 'id')
        variant_list = []
        for variant in variants:
            # Get dynamic options for this variant
            dynamic_options = []
            for option in variant.dynamic_options.all().order_by('position'):
                dynamic_options.append({
                    'name': option.name,
                    'value': option.value,
                    'position': option.position
                })
            
            variant_list.append({
                'id': variant.id,
                'title': variant.title,
                'sku': variant.sku,
                'price': float(variant.price) if variant.price else 0.0,
                'old_price': float(variant.old_price) if variant.old_price else None,
                'quantity': variant.quantity,
                'track_quantity': variant.track_quantity,
                'allow_backorder': variant.allow_backorder,
                'weight_unit': variant.weight_unit,
                'position': variant.position,
                'is_active': variant.is_active,
                'dynamic_options': dynamic_options
            })
        
        # Prepare response data
        product_data = {
            'id': product.id,
            'title': product.title,
            'slug': product.slug,
            'description': product.description,
            'short_description': product.short_description,
            'meta_title': product.meta_title,
            'meta_description': product.meta_description,
            'category': {
                'id': product.category.id if product.category else None,
                'name': product.category.name if product.category else None,
                'slug': product.category.slug if product.category else None,
            } if product.category else None,
            'subcategory': {
                'id': product.subcategory.id if product.subcategory else None,
                'name': product.subcategory.name if product.subcategory else None,
                'slug': product.subcategory.slug if product.subcategory else None,
            } if product.subcategory else None,
            'product_type': product.product_type,
            'status': product.status,
            'price': float(product.price) if product.price else 0.0,
            'old_price': float(product.old_price) if product.old_price else None,
            'quantity': product.quantity,
            'track_quantity': product.track_quantity,
            'allow_backorder': product.allow_backorder,
            'weight': product.weight,
            'weight_unit': product.weight_unit,
            'requires_shipping': product.requires_shipping,
            'taxable': product.taxable,
            'featured': product.featured,
            'tags': product.tags,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat(),
            'images': image_list,
            'variants': variant_list,
            'primary_image': image_list[0] if image_list else None,
            'total_images': len(image_list),
            'total_variants': len(variant_list)
        }
        
        return Response({
            'success': True,
            'product': product_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
