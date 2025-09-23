from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views
from .views import CategoryViewSet, SubCategoryViewSet, ProductViewSet
from .views.products.homepage import homepage_products
from .views.products.get_single_product import get_single_product
from .views.products.product_reviews import get_product_reviews, create_product_review
from .views.search.search import SearchViewSet

# Create router for ViewSets
router = DefaultRouter()

# Register ViewSets with router
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'subcategory', SubCategoryViewSet, basename='subcategory')
router.register(r'product', ProductViewSet, basename='product')
router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    # Homepage API
    path('homepage/', homepage_products, name='homepage-products'),
    # Single Product API
    path('product-detail/<slug:slug>/', get_single_product, name='single-product'),
    # Product Reviews API
    path('product-reviews/<slug:slug>/', get_product_reviews, name='product-reviews'),
    path('product-reviews/<slug:slug>/create/', create_product_review, name='create-review'),
]
