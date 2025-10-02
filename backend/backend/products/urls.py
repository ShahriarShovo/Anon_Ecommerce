from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views
from .views import CategoryViewSet, SubCategoryViewSet, ProductViewSet
from .views.products.homepage import homepage_products
from .views.products.get_single_product import get_single_product
from .views.products.product_reviews import get_product_reviews, create_product_review
from .views.products.purchase_verification import check_purchase_eligibility, get_user_purchase_history
from .views.search.search import SearchViewSet
from .views.filters.price_filter import PriceFilterViewSet
from .views.pagination.home_pagination import HomePaginationViewSet
from .views.search.product_search_views import (
    ProductSearchView,
    search_suggestions,
    filter_options
)

# Create router for ViewSets
router = DefaultRouter()

# Register ViewSets with router
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'subcategory', SubCategoryViewSet, basename='subcategory')
router.register(r'product', ProductViewSet, basename='product')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'price-filter', PriceFilterViewSet, basename='price-filter')
router.register(r'pagination', HomePaginationViewSet, basename='pagination')

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
    # Purchase Verification API
    path('purchase-verification/<slug:slug>/', check_purchase_eligibility, name='check-purchase-eligibility'),
    path('purchase-history/<slug:slug>/', get_user_purchase_history, name='user-purchase-history'),
    # Advanced Search API
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('search/suggestions/', search_suggestions, name='search_suggestions'),
    path('search/filter-options/', filter_options, name='filter_options'),
]
