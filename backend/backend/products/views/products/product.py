from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import Product, ProductVariant, ProductImage
from products.serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductVariantSerializer, ProductImageSerializer
)
from products.permissions import IsAdminOrStaffOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category', 'subcategory').prefetch_related('images', 'variants')
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'subcategory', 'product_type', 'featured']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'subcategory').prefetch_related(
            'variants', 'images'
        )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by subcategory
        subcategory = self.request.query_params.get('subcategory', None)
        if subcategory:
            queryset = queryset.filter(subcategory__slug=subcategory)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock status
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(quantity__gt=0)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(quantity=0)
        
        return queryset

    @swagger_auto_schema(
        operation_description="Get all active products",
        responses={200: ProductListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active products"""
        active_products = self.get_queryset().filter(status='active')
        serializer = ProductListSerializer(active_products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get featured products",
        responses={200: ProductListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(featured=True, status='active')
        serializer = ProductListSerializer(featured_products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get products by category",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Category slug",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: ProductListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products by category"""
        category_slug = request.query_params.get('category')
        if not category_slug:
            return Response(
                {'error': 'Category parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = self.get_queryset().filter(category__slug=category_slug, status='active')
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get product variants",
        responses={200: ProductVariantSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def variants(self, request, slug=None):
        """Get product variants"""
        try:
            product = Product.objects.get(slug=slug)
            variants = product.variants.all()
            serializer = ProductVariantSerializer(variants, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Get product images",
        responses={200: ProductImageSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def images(self, request, slug=None):
        """Get product images"""
        try:
            product = Product.objects.get(slug=slug)
            images = product.images.all()
            serializer = ProductImageSerializer(images, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Update product status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'active', 'archived'])
            }
        ),
        responses={200: ProductDetailSerializer}
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, slug=None):
        """Update product status"""
        try:
            product = Product.objects.get(slug=slug)
            new_status = request.data.get('status')
            
            if new_status not in ['draft', 'active', 'archived']:
                return Response(
                    {'error': 'Invalid status. Must be draft, active, or archived'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.status = new_status
            if new_status == 'active' and not product.published_at:
                from django.utils import timezone
                product.published_at = timezone.now()
            product.save()
            
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Bulk update product status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'active', 'archived'])
            }
        ),
        responses={200: {'message': 'Products updated successfully'}}
    )
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        """Bulk update product status"""
        product_ids = request.data.get('product_ids', [])
        new_status = request.data.get('status')
        
        if not product_ids or not new_status:
            return Response(
                {'error': 'product_ids and status are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in ['draft', 'active', 'archived']:
            return Response(
                {'error': 'Invalid status. Must be draft, active, or archived'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = Product.objects.filter(id__in=product_ids).update(status=new_status)
        
        return Response({
            'message': f'Successfully updated {updated_count} products',
            'updated_count': updated_count
        })
