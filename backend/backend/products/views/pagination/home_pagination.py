from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from products.models import Product
from products.serializers import ProductListSerializer

class HomePaginationViewSet(viewsets.ViewSet):
    """
    Pagination functionality for home page products
    """

    @swagger_auto_schema(
        operation_description="Get paginated products for home page with optional filters",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER,
                default=12
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter by category slug",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'subcategory',
                openapi.IN_QUERY,
                description="Filter by subcategory slug",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'min_price',
                openapi.IN_QUERY,
                description="Minimum price",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'max_price',
                openapi.IN_QUERY,
                description="Maximum price",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'sort',
                openapi.IN_QUERY,
                description="Sort by field (price, created_at, title)",
                type=openapi.TYPE_STRING,
                enum=['price', 'created_at', 'title', '-price', '-created_at', '-title']
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful retrieval of paginated products",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='products')
    def get_paginated_products(self, request):
        """
        Get paginated products for home page with optional filters
        """

        # Base queryset - only active products
        queryset = Product.objects.filter(status='active').select_related('category', 'subcategory').prefetch_related('images')
        
        filters_applied = {}
        
        # Search filter
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
            filters_applied['search'] = search_query
        
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
        
        # Price range filters
        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(price__gte=min_price)
                filters_applied['min_price'] = min_price
            except ValueError:
                pass
        
        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(price__lte=max_price)
                filters_applied['max_price'] = max_price
            except ValueError:
                pass
        
        # Sorting
        sort_by = request.query_params.get('sort', '-created_at')
        if sort_by in ['price', 'created_at', 'title', '-price', '-created_at', '-title']:
            queryset = queryset.order_by(sort_by)
            filters_applied['sort'] = sort_by
        else:
            queryset = queryset.order_by('-created_at')
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 12))
        page = int(request.query_params.get('page', 1))
        
        # Ensure page_size is reasonable
        if page_size > 50:
            page_size = 50
        elif page_size < 1:
            page_size = 12
        
        # Ensure page is valid
        if page < 1:
            page = 1
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Ensure page doesn't exceed total pages
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        start = (page - 1) * page_size
        end = start + page_size
        
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
            'current_page': page,
            'total_pages': total_pages,
            'page_size': page_size,
            'filters_applied': filters_applied
        }
        
        # Add pagination links
        if page < total_pages:
            next_page = page + 1
            response_data['next'] = f"?page={next_page}&page_size={page_size}"
        else:
            response_data['next'] = None
            
        if page > 1:
            previous_page = page - 1
            response_data['previous'] = f"?page={previous_page}&page_size={page_size}"
        else:
            response_data['previous'] = None
        
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get pagination info without products (for pagination UI)",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER,
                default=12
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful retrieval of pagination info",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='pagination-info')
    def get_pagination_info(self, request):
        """
        Get pagination information without products (for pagination UI)
        """
        # Base queryset - only active products
        queryset = Product.objects.filter(status='active')
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 12))
        page = int(request.query_params.get('page', 1))
        
        # Ensure page_size is reasonable
        if page_size > 50:
            page_size = 50
        elif page_size < 1:
            page_size = 12
        
        # Ensure page is valid
        if page < 1:
            page = 1
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Ensure page doesn't exceed total pages
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        response_data = {
            'count': total_count,
            'current_page': page,
            'total_pages': total_pages,
            'page_size': page_size
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
