from rest_framework import serializers
from products.models import SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = [
            'id', 'category', 'category_name', 'category_slug', 'name', 'slug', 'description', 
            'image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class SubCategoryListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'category_slug', 'name', 'slug', 'image', 'is_active']

class SubCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'image', 'is_active']
