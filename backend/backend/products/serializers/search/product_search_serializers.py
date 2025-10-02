"""
Product Search Serializers
Handles serialization for search, filter, and sort operations
"""

from rest_framework import serializers
from products.models import Product


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer for search results with optimized fields"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'old_price',
            'category_name', 'primary_image_url', 'status', 'quantity',
            'average_rating', 'review_count', 'created_at', 'updated_at',
            'featured'
        ]
    
    def get_primary_image_url(self, obj):
        """Get primary image URL"""
        primary_image = obj.primary_image
        if primary_image and hasattr(primary_image, 'image_url'):
            return primary_image.image_url
        return None
    
    def get_average_rating(self, obj):
        """Get average rating"""
        return getattr(obj, 'average_rating', 0.0)
    
    def get_review_count(self, obj):
        """Get review count"""
        return getattr(obj, 'review_count', 0)


class SearchSuggestionSerializer(serializers.Serializer):
    """Serializer for search suggestions"""
    
    text = serializers.CharField()
    type = serializers.CharField()  # 'product', 'category', 'sku'
    count = serializers.IntegerField()


class FilterOptionSerializer(serializers.Serializer):
    """Serializer for filter options"""
    
    value = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class ProductSearchResponseSerializer(serializers.Serializer):
    """Serializer for search response"""
    
    results = ProductSearchSerializer(many=True)
    total_count = serializers.IntegerField()
    current_page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    search_term = serializers.CharField(required=False)
    applied_filters = serializers.DictField(required=False)
    sort_by = serializers.CharField(required=False)
    sort_order = serializers.CharField(required=False)
