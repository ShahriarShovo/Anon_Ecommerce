from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views
from .views import CategoryViewSet, SubCategoryViewSet, ProductViewSet

# Create router for ViewSets
router = DefaultRouter()

# Register ViewSets with router
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'subcategory', SubCategoryViewSet, basename='subcategory')
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]
