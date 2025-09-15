from rest_framework import serializers
from products.models import Product, ProductVariant, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'caption', 'position', 'is_primary']
        read_only_fields = ['id', 'image_url']
    
    def get_image_url(self, obj):
        return obj.image_url

class ProductVariantSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.BooleanField(read_only=True)
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    option_values = serializers.ListField(read_only=True)
    option_names = serializers.ListField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'sku', 'barcode', 'price', 'compare_at_price', 'cost_per_item',
            'quantity', 'track_quantity', 'allow_backorder', 'weight', 'weight_unit',
            'option1_name', 'option1_value', 'option2_name', 'option2_value',
            'option3_name', 'option3_value', 'position', 'is_active',
            'is_in_stock', 'display_price', 'discount_percentage', 'option_values', 'option_names',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_inventory = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_variable = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'product_type', 'status', 'price', 'compare_at_price',
            'min_price', 'max_price', 'total_inventory', 'is_in_stock', 'is_variable',
            'featured', 'tags', 'primary_image', 'variant_count',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        primary_image = obj.primary_image
        if primary_image:
            return {
                'id': primary_image.id,
                'image': primary_image.image.url if primary_image.image else None,
                'image_url': primary_image.image_url,
                'alt_text': primary_image.alt_text,
                'caption': primary_image.caption,
                'position': primary_image.position,
                'is_primary': primary_image.is_primary
            }
        return None
    
    def get_variant_count(self, obj):
        return obj.variants.count()

class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_inventory = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_variable = serializers.BooleanField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'meta_title', 'meta_description', 'category', 'category_name',
            'subcategory', 'subcategory_name', 'product_type', 'status',
            'price', 'compare_at_price', 'cost_per_item', 'track_quantity',
            'quantity', 'allow_backorder', 'quantity_policy', 'weight',
            'weight_unit', 'requires_shipping', 'taxable', 'featured',
            'tags', 'min_price', 'max_price', 'total_inventory', 'is_in_stock',
            'is_variable', 'images', 'variants', 'created_at', 'updated_at',
            'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for product create/update operations"""
    variants = ProductVariantSerializer(many=True, required=False, read_only=True)
    images = ProductImageSerializer(many=True, required=False, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'short_description', 'meta_title', 'meta_description',
            'category', 'subcategory', 'product_type', 'status', 'price', 'compare_at_price',
            'cost_per_item', 'track_quantity', 'quantity', 'allow_backorder',
            'quantity_policy', 'weight', 'weight_unit', 'requires_shipping',
            'taxable', 'featured', 'tags', 'variants', 'images', 'uploaded_images'
        ]
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        variants_data = validated_data.pop('variants', [])
        images_data = validated_data.pop('images', [])
        
        product = Product.objects.create(**validated_data)
        
        # Handle uploaded images
        for i, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                position=i + 1,
                is_primary=(i == 0)  # First image is primary
            )
        
        # Handle existing images data
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        # Create variants
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)
        
        return product
    
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        variants_data = validated_data.pop('variants', [])
        images_data = validated_data.pop('images', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle new uploaded images
        if uploaded_images:
            # Get current max position
            from django.db import models
            max_position = instance.images.aggregate(
                max_pos=models.Max('position')
            )['max_pos'] or 0
            
            for i, image in enumerate(uploaded_images):
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    position=max_position + i + 1,
                    is_primary=False  # Don't make new images primary by default
                )
        
        # Handle existing images data (simple replace for now)
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        # Update variants (delete existing and create new ones)
        if variants_data:
            instance.variants.all().delete()
            for variant_data in variants_data:
                ProductVariant.objects.create(product=instance, **variant_data)
        
        return instance
