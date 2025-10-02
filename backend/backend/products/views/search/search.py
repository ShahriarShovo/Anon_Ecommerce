from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Min, Max, F
from django.db.models.functions import Coalesce
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import Product
from products.serializers import ProductListSerializer

class SearchViewSet(viewsets.ViewSet):
    """
    Search functionality for products
    """
    
    @swagger_auto_schema(
        operation_description="Search products by name, description, or tags",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING,
                required=True
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
                description="Search results",
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
                        'query': openapi.Schema(type=openapi.TYPE_STRING),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(description="Bad request - missing search query")
        }
    )
    @action(detail=False, methods=['get'], url_path='products')
    def search_products(self, request):
        """
        Search products by query string with optional filters
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Base queryset - only active products
        queryset = Product.objects.filter(status='active')
        
        # Search in title, description, and tags
        search_query = Q(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
        
        queryset = queryset.filter(search_query)
        
        # Apply filters
        filters_applied = {}
        
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
        
        # Price range filters aligned with variants and simple prices
        # Annotate effective bounds: per product, min/max across variants or fallback to product.price
        queryset = queryset.annotate(
            effective_min_price=Coalesce(Min('variants__price'), F('price')),
            effective_max_price=Coalesce(Max('variants__price'), F('price')),
        )

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

        if min_val is not None and max_val is not None:
            queryset = queryset.filter(
                effective_min_price__gte=min_val,
                effective_max_price__lte=max_val,
            )
        elif min_val is not None:
            queryset = queryset.filter(effective_min_price__gte=min_val)
        elif max_val is not None:
            queryset = queryset.filter(effective_max_price__lte=max_val)
        
        # Order by created_at for now (simplified)
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
                    product_data['primary_image']['image_url'] = f"http://127.0.0.1:8000{product_data['primary_image']['image_url']}"
        
        # Prepare response data
        response_data = {
            'results': serializer.data,
            'count': total_count,
            'query': query,
            'filters_applied': filters_applied,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
        
        # Add pagination links
        if end < total_count:
            next_page = page + 1
            response_data['next'] = f"?q={query}&page={next_page}&page_size={page_size}"
            if category_slug:
                response_data['next'] += f"&category={category_slug}"
            if subcategory_slug:
                response_data['next'] += f"&subcategory={subcategory_slug}"
            if min_price:
                response_data['next'] += f"&min_price={min_price}"
            if max_price:
                response_data['next'] += f"&max_price={max_price}"
        
        if page > 1:
            prev_page = page - 1
            response_data['previous'] = f"?q={query}&page={prev_page}&page_size={page_size}"
            if category_slug:
                response_data['previous'] += f"&category={category_slug}"
            if subcategory_slug:
                response_data['previous'] += f"&subcategory={subcategory_slug}"
            if min_price:
                response_data['previous'] += f"&min_price={min_price}"
            if max_price:
                response_data['previous'] += f"&max_price={max_price}"
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Get search suggestions based on partial query",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Partial search query",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Maximum number of suggestions",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Search suggestions",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'suggestions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'query': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='suggestions')
    def search_suggestions(self, request):
        """
        Get search suggestions based on partial query
        """
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 5))
        
        if not query or len(query) < 2:
            return Response({
                'suggestions': [],
                'query': query
            })
        
        # Get product titles that match the query
        suggestions = Product.objects.filter(
            status='active',
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:limit]
        
        # Get category names that match the query
        from products.models import Category
        category_suggestions = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True).distinct()[:limit]
        
        # Combine and deduplicate suggestions
        all_suggestions = list(suggestions) + list(category_suggestions)
        unique_suggestions = list(dict.fromkeys(all_suggestions))[:limit]
        
        return Response({
            'suggestions': unique_suggestions,
            'query': query
        })
