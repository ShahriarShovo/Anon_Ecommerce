"""
Product Search Views
Handles search, filter, and sort operations for products
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Min, Max
from django.core.paginator import Paginator
from products.models import Product, Category
from products.serializers.search.product_search_serializers import (
    ProductSearchSerializer,
    SearchSuggestionSerializer,
    FilterOptionSerializer,
    ProductSearchResponseSerializer
)


class ProductSearchView(generics.ListAPIView):
    """
    Advanced product search with filtering and sorting
    """
    serializer_class = ProductSearchSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get filtered and sorted queryset"""
        queryset = Product.objects.select_related('category', 'subcategory').prefetch_related('images', 'variants', 'reviews')
        
        # Search term filtering (support both 'q' and 'search' parameters)
        search_term = self.request.query_params.get('q', '').strip() or self.request.query_params.get('search', '').strip()
        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(category__name__icontains=search_term) |
                Q(variants__sku__icontains=search_term)
            ).distinct()
        
        # Category filtering
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Status filtering
        status_filter = self.request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Featured filtering
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        elif featured == 'false':
            queryset = queryset.filter(featured=False)
        
        # Stock filtering
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(quantity__gt=0)
        elif in_stock == 'false':
            queryset = queryset.filter(quantity=0)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Custom list method with pagination and response formatting"""
        queryset = self.get_queryset()
        
        # Sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        sort_order = request.query_params.get('sort_order', 'desc')
        
        valid_sort_fields = ['title', 'price', 'created_at', 'updated_at', 'quantity']
        if sort_by in valid_sort_fields:
            if sort_order == 'desc':
                queryset = queryset.order_by(f'-{sort_by}')
            else:
                queryset = queryset.order_by(sort_by)
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize results
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        # Prepare response data
        response_data = {
            'results': serializer.data,
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'search_term': request.query_params.get('q', '') or request.query_params.get('search', ''),
            'applied_filters': {
                'category': request.query_params.get('category'),
                'status': request.query_params.get('status'),
                'min_price': request.query_params.get('min_price'),
                'max_price': request.query_params.get('max_price'),
                'featured': request.query_params.get('featured'),
                'in_stock': request.query_params.get('in_stock'),
            },
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def search_suggestions(request):
    """
    Get search suggestions based on partial input
    """
    query = request.query_params.get('q', '').strip()
    
    if len(query) < 2:
        return Response({'suggestions': []})
    
    suggestions = []
    
    # Product title suggestions
    product_titles = Product.objects.filter(
        title__icontains=query
    ).values_list('title', flat=True)[:5]
    
    for title in product_titles:
        suggestions.append({
            'text': title,
            'type': 'product',
            'count': 1
        })
    
    # Category suggestions
    categories = Category.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:3]
    
    for category in categories:
        suggestions.append({
            'text': category,
            'type': 'category',
            'count': 1
        })
    
    # SKU suggestions
    skus = Product.objects.filter(
        sku__icontains=query
    ).values_list('sku', flat=True)[:3]
    
    for sku in skus:
        suggestions.append({
            'text': sku,
            'type': 'sku',
            'count': 1
        })
    
    return Response({'suggestions': suggestions})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def filter_options(request):
    """
    Get available filter options
    """
    # Category options
    category_options = Category.objects.annotate(
        product_count=Count('products')
    ).values('slug', 'name', 'product_count')
    
    # Status options
    status_options = Product.objects.values('status').annotate(
        count=Count('id')
    ).values('status', 'count')
    
    # Price range options
    price_stats = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Featured options
    featured_count = Product.objects.filter(featured=True).count()
    non_featured_count = Product.objects.filter(featured=False).count()
    
    # Stock options
    in_stock_count = Product.objects.filter(quantity__gt=0).count()
    out_of_stock_count = Product.objects.filter(quantity=0).count()
    
    return Response({
        'categories': [
            {'value': cat['slug'], 'label': cat['name'], 'count': cat['product_count']}
            for cat in category_options
        ],
        'statuses': [
            {'value': status['status'], 'label': status['status'].title(), 'count': status['count']}
            for status in status_options
        ],
        'price_range': {
            'min': price_stats['min_price'] or 0,
            'max': price_stats['max_price'] or 0
        },
        'featured': [
            {'value': 'true', 'label': 'Featured', 'count': featured_count},
            {'value': 'false', 'label': 'Not Featured', 'count': non_featured_count}
        ],
        'stock': [
            {'value': 'true', 'label': 'In Stock', 'count': in_stock_count},
            {'value': 'false', 'label': 'Out of Stock', 'count': out_of_stock_count}
        ]
    })
