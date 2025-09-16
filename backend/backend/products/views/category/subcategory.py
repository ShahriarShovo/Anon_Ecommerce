from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import SubCategory
from products.serializers import SubCategorySerializer, SubCategoryListSerializer, SubCategoryCreateUpdateSerializer
from products.permissions import IsAdminOrStaffOrReadOnly

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return SubCategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SubCategoryCreateUpdateSerializer
        return SubCategorySerializer

    def get_queryset(self):
        queryset = SubCategory.objects.select_related('category')
        category_slug = self.request.query_params.get('category', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset

    @swagger_auto_schema(
        operation_description="Get all active subcategories",
        responses={200: SubCategoryListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active subcategories"""
        active_subcategories = SubCategory.objects.filter(is_active=True).select_related('category')
        serializer = SubCategoryListSerializer(active_subcategories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get subcategories by category",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Category slug",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: SubCategoryListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get subcategories by category slug"""
        category_slug = request.query_params.get('category')
        if not category_slug:
            return Response(
                {'error': 'Category parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subcategories = SubCategory.objects.filter(
            category__slug=category_slug, 
            is_active=True
        ).select_related('category')
        
        serializer = SubCategoryListSerializer(subcategories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get subcategory details",
        responses={200: SubCategorySerializer}
    )
    def retrieve(self, request, slug=None):
        """Get subcategory details"""
        try:
            subcategory = SubCategory.objects.select_related('category').get(slug=slug)
            serializer = SubCategorySerializer(subcategory)
            return Response(serializer.data)
        except SubCategory.DoesNotExist:
            return Response(
                {'error': 'SubCategory not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
