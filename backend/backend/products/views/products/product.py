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

    def create(self, request, *args, **kwargs):
        """Custom create method to handle FormData with variants"""
        print(f"Content-Type: {request.content_type}")
        print(f"Request data keys: {list(request.data.keys())}")
        print(f"Request data type: {type(request.data)}")
        
        # Check if we have variant data in FormData
        has_variants = any(key.startswith('variants[') for key in request.data.keys())
        print(f"Has variant keys: {has_variants}")
        
        # Parse FormData manually for variants
        if request.content_type and 'multipart/form-data' in request.content_type and has_variants:
            # Extract variants data from FormData
            variants_data = []
            variant_index = 0
            
            while True:
                variant_key = f'variants[{variant_index}][title]'
                print(f"Looking for variant key: {variant_key}")
                print(f"Available keys: {[k for k in request.data.keys() if k.startswith(f'variants[{variant_index}]')]}")
                if variant_key not in request.data:
                    print(f"Variant key {variant_key} not found, breaking")
                    break
                
                variant_data = {}
                print(f"Processing variant {variant_index}")
                
                # Extract basic variant fields with proper data handling
                for key, value in request.data.items():
                    if key.startswith(f'variants[{variant_index}]') and not key.startswith(f'variants[{variant_index}][dynamic_options]'):
                        field_name = key.split(']')[1][1:]  # Remove 'variants[index][' and ']'
                        print(f"Processing field: {field_name} = {value}")
                        
                        # Skip problematic fields
                        if field_name not in ['options']:
                            # Get the actual value (handle both single values and lists)
                            actual_value = value[0] if isinstance(value, list) and value else value
                            
                            # Skip empty values for optional fields
                            if not actual_value and field_name not in ['title', 'price']:
                                continue
                            
                            # Convert string values to appropriate types
                            if field_name in ['price', 'old_price', 'weight']:
                                try:
                                    if actual_value:
                                        variant_data[field_name] = float(actual_value)
                                    elif field_name == 'price':
                                        # Price is required, set to 0 if empty
                                        variant_data[field_name] = 0.0
                                except (ValueError, TypeError):
                                    if field_name == 'price':
                                        variant_data[field_name] = 0.0
                            elif field_name in ['quantity', 'position']:
                                try:
                                    if actual_value:
                                        variant_data[field_name] = int(actual_value)
                                    else:
                                        variant_data[field_name] = 0 if field_name == 'quantity' else 1
                                except (ValueError, TypeError):
                                    variant_data[field_name] = 0 if field_name == 'quantity' else 1
                            elif field_name in ['track_quantity', 'allow_backorder', 'is_active']:
                                variant_data[field_name] = str(actual_value).lower() == 'true' if actual_value else False
                            else:
                                variant_data[field_name] = str(actual_value) if actual_value else ''
                
                # Extract dynamic options
                dynamic_options = []
                option_index = 0
                while True:
                    option_name_key = f'variants[{variant_index}][dynamic_options][{option_index}][name]'
                    if option_name_key not in request.data:
                        break
                    
                    # Get actual values properly
                    name_data = request.data.get(option_name_key, [''])
                    name_value = name_data[0] if name_data and len(name_data) > 0 else ''
                    print(f"Option name key: {option_name_key}, Raw data: {name_data}, Parsed value: '{name_value}'")
                    
                    value_key = f'variants[{variant_index}][dynamic_options][{option_index}][value]'
                    value_data = request.data.get(value_key, [''])
                    value_value = value_data[0] if value_data and len(value_data) > 0 else ''
                    print(f"Option value key: {value_key}, Raw data: {value_data}, Parsed value: '{value_value}'")
                    
                    position_key = f'variants[{variant_index}][dynamic_options][{option_index}][position]'
                    position_data = request.data.get(position_key, [option_index + 1])
                    position_value = position_data[0] if position_data and len(position_data) > 0 else option_index + 1
                    
                    option_data = {
                        'name': str(name_value),
                        'value': str(value_value),
                        'position': int(position_value) if position_value else option_index + 1
                    }
                    dynamic_options.append(option_data)
                    option_index += 1
                
                if dynamic_options:
                    variant_data['dynamic_options'] = dynamic_options
                
                variants_data.append(variant_data)
                variant_index += 1
            
            # Add variants to request data
            if variants_data:
                print(f"Adding variants_data to request: {variants_data}")
                # Create a mutable copy of request.data
                from django.http import QueryDict
                mutable_data = QueryDict('', mutable=True)
                
                # Copy all existing data
                for key, value in request.data.items():
                    if isinstance(value, list):
                        for v in value:
                            mutable_data.appendlist(key, v)
                    else:
                        mutable_data[key] = value
                
                # Store variants data separately for serializer to use
                request._variants_data = variants_data
                
                # Store mutable data for serializer to use
                request._mutable_data = mutable_data
                
                print(f"Successfully added variants to mutable request.data")
            else:
                print("No variants_data found")
        
        # Debug: Check what data is being passed to serializer
        print(f"Final request.data before serializer: {dict(request.data)}")
        print(f"Variants in request.data: {request.data.get('variants', 'NOT_FOUND')}")
        
        # Use custom data if available
        if hasattr(request, '_mutable_data') and hasattr(request, '_variants_data'):
            print(f"Using custom mutable data with variants: {request._variants_data}")
            
            # Convert QueryDict to regular dict and add variants
            serializer_data = {}
            for key, value in request._mutable_data.items():
                if key.startswith('variants['):
                    continue  # Skip FormData variant keys
                serializer_data[key] = value
            
            # Add the parsed variants data
            serializer_data['variants'] = request._variants_data
            
            # Handle uploaded_images properly - only include actual files
            uploaded_images = []
            print(f"Processing uploaded_images from request._mutable_data")
            for key, value in request._mutable_data.items():
                print(f"Key: {key}, Value type: {type(value)}, Has read method: {hasattr(value, 'read') if value else 'N/A'}")
                if key == 'uploaded_images' and hasattr(value, 'read'):  # It's a file
                    uploaded_images.append(value)
                    print(f"Added file: {value}")
            
            # Also check request.FILES for uploaded_images
            print(f"Request.FILES: {request.FILES}")
            for key, value in request.FILES.items():
                if key == 'uploaded_images':
                    uploaded_images.append(value)
                    print(f"Added file from FILES: {value}")
            
            serializer_data['uploaded_images'] = uploaded_images
            print(f"Final uploaded_images: {uploaded_images}")
            
            print(f"Serializer data structure: {serializer_data}")
            
            serializer = self.get_serializer(data=serializer_data)
            print(f"Serializer data before validation: {serializer_data}")
            if not serializer.is_valid():
                print(f"Serializer validation errors: {serializer.errors}")
                # Return only the first few errors to avoid huge response
                error_summary = {}
                for field, errors in serializer.errors.items():
                    if len(errors) > 5:
                        error_summary[field] = errors[:5] + [f"... and {len(errors) - 5} more errors"]
                    else:
                        error_summary[field] = errors
                return Response(error_summary, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"Error in create method: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method to handle product deletion with order references"""
        try:
            instance = self.get_object()
            
            # Check if product is referenced in any orders
            from orders.models import OrderItem
            order_items = OrderItem.objects.filter(product=instance)
            
            if order_items.exists():
                # If product is in orders, archive it instead of deleting
                instance.status = 'archived'
                instance.save()
                
                return Response({
                    'message': 'Product archived successfully. Cannot delete due to existing orders.',
                    'archived': True,
                    'order_count': order_items.count()
                }, status=status.HTTP_200_OK)
            else:
                # If no orders reference this product, delete it
                self.perform_destroy(instance)
                return Response({
                    'message': 'Product deleted successfully.',
                    'deleted': True
                }, status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            return Response({
                'error': f'Failed to delete product: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
