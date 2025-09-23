from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import Category
from products.serializers import CategorySerializer, CategoryListSerializer, CategoryCreateUpdateSerializer
from products.permissions import IsAdminOrStaffOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @swagger_auto_schema(
        operation_description="Get all active categories",
        responses={200: CategoryListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active categories"""
        active_categories = Category.objects.filter(is_active=True)
        serializer = CategoryListSerializer(active_categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get category with subcategories",
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, slug=None):
        """Get category details with subcategories"""
        try:
            category = Category.objects.prefetch_related('subcategories').get(slug=slug)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Get subcategories for a specific category",
        responses={200: openapi.Response('Subcategories list', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subcategories': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            }
        ))}
    )
    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """Get subcategories for a specific category"""
        try:
            category = Category.objects.get(slug=slug)
            subcategories = category.subcategories.filter(is_active=True)
            subcategories_data = []
            for subcat in subcategories:
                subcategories_data.append({
                    'id': subcat.id,
                    'name': subcat.name,
                    'slug': subcat.slug,
                    'image': subcat.image.url if subcat.image else None,
                })
            return Response({'subcategories': subcategories_data})
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
