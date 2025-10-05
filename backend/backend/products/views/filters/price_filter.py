from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Min, Max, F
from django.db.models.functions import Coalesce
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

from products.models import Product
from products.serializers import ProductListSerializer

class PriceFilterViewSet(viewsets.ViewSet):
    """
    Price filtering functionality for products
    """
    
    @swagger_auto_schema(
        operation_description="Filter products by price range",
        manual_parameters=[
            openapi.Parameter(
                'min_price',
                openapi.IN_QUERY,
                description="Minimum price filter",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
            openapi.Parameter(
                'max_price',
                openapi.IN_QUERY,
                description="Maximum price filter",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter by category slug",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'subcategory',
                openapi.IN_QUERY,
                description="Filter by subcategory slug",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Filtered products by price",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='products')
    def filter_by_price(self, request):
        """
        Filter products by price range with optional category filters
        """
        # Base queryset - only active products
        queryset = Product.objects.filter(status='active')
        
        # Apply filters
        filters_applied = {}
        
        # Price range filters - use simple price filtering
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        min_val = None
        max_val = None
        try:
            if min_price is not None and min_price != '':
                min_val = float(min_price)
                filters_applied['min_price'] = min_val
        except ValueError:
            min_val = None
        try:
            if max_price is not None and max_price != '':
                max_val = float(max_price)
                filters_applied['max_price'] = max_val
        except ValueError:
            max_val = None

        # Apply simple price range filters
        if min_val is not None and max_val is not None:
            # Show products where the main price is within the range
            queryset = queryset.filter(price__gte=min_val, price__lte=max_val)
        elif min_val is not None:
            # Show products where the main price is >= min
            queryset = queryset.filter(price__gte=min_val)
        elif max_val is not None:
            # Show products where the main price is <= max
            queryset = queryset.filter(price__lte=max_val)
        
        # Category filter
        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            filters_applied['category'] = category_slug
        
        # Subcategory filter
        subcategory_slug = request.query_params.get('subcategory')
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
            filters_applied['subcategory'] = subcategory_slug
        
        # Order by created_at
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 12))
        page = int(request.query_params.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        products = queryset[start:end]
        
        # Serialize products
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        
        # Fix image URLs to be absolute
        for product_data in serializer.data:
            if product_data.get('primary_image') and product_data['primary_image'].get('image_url'):
                if not product_data['primary_image']['image_url'].startswith('http'):
                    product_data['primary_image']['image_url'] = f"{settings.BACKEND_BASE_URL}{product_data['primary_image']['image_url']}"
        
        # Prepare response data
        response_data = {
            'results': serializer.data,
            'count': total_count,
            'filters_applied': filters_applied,
            'page': page,
            'current_page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
        
        # Add pagination links
        if end < total_count:
            next_page = page + 1
            response_data['next'] = f"?page={next_page}&page_size={page_size}"
            if min_price:
                response_data['next'] += f"&min_price={min_price}"
            if max_price:
                response_data['next'] += f"&max_price={max_price}"
            if category_slug:
                response_data['next'] += f"&category={category_slug}"
            if subcategory_slug:
                response_data['next'] += f"&subcategory={subcategory_slug}"
        
        if page > 1:
            prev_page = page - 1
            response_data['previous'] = f"?page={prev_page}&page_size={page_size}"
            if min_price:
                response_data['previous'] += f"&min_price={min_price}"
            if max_price:
                response_data['previous'] += f"&max_price={max_price}"
            if category_slug:
                response_data['previous'] += f"&category={category_slug}"
            if subcategory_slug:
                response_data['previous'] += f"&subcategory={subcategory_slug}"
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Get price range statistics for products",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter by category slug",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'subcategory',
                openapi.IN_QUERY,
                description="Filter by subcategory slug",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Price range statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'min_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'max_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'avg_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'total_products': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='price-stats')
    def get_price_stats(self, request):
        """
        Get price range statistics for products
        """
        # Base queryset - only active products
        queryset = Product.objects.filter(status='active')
        
        # Apply category filters if provided
        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        subcategory_slug = request.query_params.get('subcategory')
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        
        # Calculate price statistics
        from django.db.models import Min, Max, Avg
        
        price_stats = queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            total_products=queryset.count()
        )
        
        return Response(price_stats, status=status.HTTP_200_OK)
