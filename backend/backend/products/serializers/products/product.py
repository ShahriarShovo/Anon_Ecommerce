from rest_framework import serializers
from products.models import Product, ProductVariant, ProductImage, VariantOption

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'caption', 'position', 'is_primary']
        read_only_fields = ['id', 'image_url']
    
    def get_image_url(self, obj):
        return obj.image_url
    
    def to_representation(self, instance):
        if instance is None:
            return None
        return super().to_representation(instance)

class VariantOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantOption
        fields = ['id', 'name', 'value', 'position']
        read_only_fields = ['id']

class ProductVariantSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.BooleanField(read_only=True)
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    option_values = serializers.ListField(read_only=True)
    option_names = serializers.ListField(read_only=True)
    dynamic_options = VariantOptionSerializer(many=True, read_only=True)
    all_options = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'sku', 'barcode', 'price', 'old_price',
            'quantity', 'track_quantity', 'allow_backorder', 'weight', 'weight_unit',
            'option1_name', 'option1_value', 'option2_name', 'option2_value',
            'option3_name', 'option3_value', 'position', 'is_active',
            'is_in_stock', 'display_price', 'discount_percentage', 'option_values', 'option_names',
            'dynamic_options', 'all_options', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_all_options(self, obj):
        """Get all options (legacy + dynamic)"""
        return obj.get_all_options()
    
    def create(self, validated_data):
        """Create variant with dynamic options"""
        dynamic_options_data = self.context.get('dynamic_options', [])
        variant = super().create(validated_data)
        
        # Set dynamic options
        if dynamic_options_data:
            variant.set_dynamic_options(dynamic_options_data)
        
        return variant
    
    def update(self, instance, validated_data):
        """Update variant with dynamic options"""
        dynamic_options_data = self.context.get('dynamic_options', [])
        variant = super().update(instance, validated_data)
        
        # Update dynamic options
        if dynamic_options_data is not None:
            variant.set_dynamic_options(dynamic_options_data)
        
        return variant

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
            'product_type', 'status', 'price', 'old_price',
            'option1_name', 'option2_name', 'option3_name',
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
            'price', 'old_price', 'option1_name', 'option2_name', 'option3_name',
            'track_quantity', 'quantity', 'allow_backorder', 'quantity_policy', 'weight',
            'weight_unit', 'requires_shipping', 'taxable', 'featured',
            'tags', 'min_price', 'max_price', 'total_inventory', 'is_in_stock',
            'is_variable', 'images', 'variants', 'created_at', 'updated_at',
            'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for product create/update operations"""
    variants = serializers.ListField(required=False, write_only=True, allow_empty=True)
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
            'category', 'subcategory', 'product_type', 'status', 'price', 'old_price',
            'option1_name', 'option2_name', 'option3_name',
            'track_quantity', 'quantity', 'allow_backorder',
            'quantity_policy', 'weight', 'weight_unit', 'requires_shipping',
            'taxable', 'featured', 'tags', 'images', 'uploaded_images', 'variants'
        ]
    
    def validate_variants(self, value):
        """Validate variants data"""
        print(f"Validating variants: {value}")
        if not isinstance(value, list):
            raise serializers.ValidationError("Variants must be a list")
        
        validated_variants = []
        for i, variant_data in enumerate(value):
            print(f"Validating variant {i}: {variant_data}")
            if not isinstance(variant_data, dict):
                raise serializers.ValidationError(f"Variant {i} must be a dictionary")
            
            # Validate required fields
            if 'price' not in variant_data or not variant_data['price']:
                raise serializers.ValidationError(f"Variant {i} must have a price")
            
            try:
                variant_data['price'] = float(variant_data['price'])
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Variant {i} price must be a valid number")
            
            if variant_data['price'] < 0:
                raise serializers.ValidationError(f"Variant {i} price must be non-negative")
            
            # Validate optional numeric fields
            for field in ['old_price', 'quantity', 'position', 'weight']:
                if field in variant_data and variant_data[field] is not None:
                    try:
                        if field in ['quantity', 'position']:
                            variant_data[field] = int(variant_data[field])
                        else:
                            variant_data[field] = float(variant_data[field])
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f"Variant {i} {field} must be a valid number")
            
            # Validate boolean fields
            for field in ['track_quantity', 'allow_backorder', 'is_active']:
                if field in variant_data:
                    if isinstance(variant_data[field], str):
                        variant_data[field] = variant_data[field].lower() == 'true'
                    elif not isinstance(variant_data[field], bool):
                        variant_data[field] = bool(variant_data[field])
            
            # Validate dynamic_options if present
            if 'dynamic_options' in variant_data:
                dynamic_options = variant_data['dynamic_options']
                print(f"Validating dynamic_options for variant {i}: {dynamic_options}")
                if not isinstance(dynamic_options, list):
                    raise serializers.ValidationError(f"Variant {i} dynamic_options must be a list")
                
                for j, option in enumerate(dynamic_options):
                    print(f"Validating option {j}: {option}")
                    if not isinstance(option, dict):
                        raise serializers.ValidationError(f"Variant {i} dynamic_options[{j}] must be a dictionary")
                    
                    if 'name' not in option or not option['name']:
                        raise serializers.ValidationError(f"Variant {i} dynamic_options[{j}] must have a name")
                    
                    if 'value' not in option or not option['value']:
                        raise serializers.ValidationError(f"Variant {i} dynamic_options[{j}] must have a value")
                    
                    if 'position' not in option:
                        option['position'] = j + 1
                    else:
                        try:
                            option['position'] = int(option['position'])
                        except (ValueError, TypeError):
                            option['position'] = j + 1
            
            validated_variants.append(variant_data)
        
        print(f"Validation completed. Validated variants: {validated_variants}")
        return validated_variants

    def create(self, validated_data):
        print(f"Validated data keys: {list(validated_data.keys())}")
        print(f"Validated data: {validated_data}")
        
        # Debug variants data
        variants_data = validated_data.get('variants', [])
        print(f"Variants data in create: {variants_data}")
        for i, variant in enumerate(variants_data):
            print(f"Variant {i}: {variant}")
            if 'dynamic_options' in variant:
                print(f"Variant {i} dynamic_options: {variant['dynamic_options']}")
        
        uploaded_images = validated_data.pop('uploaded_images', [])
        variants_data = validated_data.pop('variants', [])
        images_data = validated_data.pop('images', [])
        
        # Variants data should now be in validated_data from FormData parsing
        print(f"Variants data from validated_data: {variants_data}")
        
        print(f"Variants data: {variants_data}")
        print(f"Uploaded images: {uploaded_images}")
        
        try:
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
            
            # Create variants with dynamic options
            for variant_data in variants_data:
                print(f"Creating variant with data: {variant_data}")
                dynamic_options_data = variant_data.pop('dynamic_options', [])
                print(f"Dynamic options data: {dynamic_options_data}")
                
                try:
                    # Remove any None or empty string values for optional fields
                    cleaned_variant_data = {}
                    for key, value in variant_data.items():
                        if value is not None and value != '':
                            cleaned_variant_data[key] = value
                    
                    variant = ProductVariant.objects.create(product=product, **cleaned_variant_data)
                    print(f"Variant created successfully: {variant}")
                    
                    # Create dynamic options
                    if dynamic_options_data:
                        variant.set_dynamic_options(dynamic_options_data)
                        print(f"Dynamic options set successfully")
                except Exception as e:
                    print(f"Error creating variant: {e}")
                    print(f"Variant data: {variant_data}")
                    print(f"Cleaned variant data: {cleaned_variant_data}")
                    # Delete the product if variant creation fails
                    product.delete()
                    raise serializers.ValidationError(f"Error creating variant: {str(e)}")
            
            return product
            
        except Exception as e:
            print(f"Error creating product: {e}")
            import traceback
            traceback.print_exc()
            raise serializers.ValidationError(f"Error creating product: {str(e)}")
    
    def is_valid(self, raise_exception=False):
        """Override is_valid to add more debugging"""
        is_valid = super().is_valid(raise_exception=False)
        if not is_valid:
            print(f"Serializer validation errors: {self.errors}")
            if raise_exception:
                raise serializers.ValidationError(self.errors)
        return is_valid
    
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
        
        # Update variants with dynamic options (delete existing and create new ones)
        if variants_data:
            instance.variants.all().delete()
            for variant_data in variants_data:
                dynamic_options_data = variant_data.pop('dynamic_options', [])
                variant = ProductVariant.objects.create(product=instance, **variant_data)
                
                # Create dynamic options
                if dynamic_options_data:
                    variant.set_dynamic_options(dynamic_options_data)
        
        return instance
