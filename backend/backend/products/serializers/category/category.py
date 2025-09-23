from rest_framework import serializers
from products.models import Category

class CategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 
            'is_active', 'created_at', 'updated_at', 'subcategories_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_subcategories_count(self, obj):
        return obj.subcategories.filter(is_active=True).count()

class CategoryListSerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'is_active', 'subcategories_count']

    def get_subcategories_count(self, obj):
        return obj.subcategories.filter(is_active=True).count()

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
