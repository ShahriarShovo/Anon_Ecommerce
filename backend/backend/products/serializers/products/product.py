from rest_framework import serializers
from products.models import Product, ProductVariant, ProductImage, VariantOption
from django.conf import settings


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'caption', 'position', 'is_primary']
        read_only_fields = ['id', 'image_url']
    
    def get_image_url(self, obj):
        if obj.image_url:
            # Return full URL if it's a relative path
            if obj.image_url.startswith('/'):
                return f"{settings.BACKEND_BASE_URL}{obj.image_url}"
            return obj.image_url
        return None
    
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
    display_price = serializers.SerializerMethodField()
    display_old_price = serializers.SerializerMethodField()
    default_variant_in_stock = serializers.SerializerMethodField()
    default_variant = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'product_type', 'status', 'price', 'old_price',
            'option1_name', 'option2_name', 'option3_name',
            'min_price', 'max_price', 'total_inventory', 'is_in_stock', 'is_variable',
            'featured', 'tags', 'primary_image', 'variant_count',
            'display_price', 'display_old_price', 'default_variant_in_stock',
            'default_variant', 'variants',
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
    
    def get_display_price(self, obj):
        """Get display price (default variant price for variable products)"""
        return obj.get_display_price()
    
    def get_display_old_price(self, obj):
        """Get display old price (default variant old price for variable products)"""
        return obj.get_display_old_price()
    
    def get_default_variant_in_stock(self, obj):
        """Check if default variant is in stock"""
        return obj.is_default_variant_in_stock()
    
    def get_default_variant(self, obj):
        """Get default variant for variable products"""
        if obj.product_type == 'variable' and obj.default_variant:
            return ProductVariantSerializer(obj.default_variant).data
        return None
    
    def get_variants(self, obj):
        """Get all variants for variable products"""
        if obj.product_type == 'variable':
            variants = obj.variants.filter(is_active=True)
            return ProductVariantSerializer(variants, many=True).data
        return []

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
    display_price = serializers.SerializerMethodField()
    display_old_price = serializers.SerializerMethodField()
    default_variant_in_stock = serializers.SerializerMethodField()
    
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
            'is_variable', 'images', 'variants', 'display_price', 'display_old_price',
            'default_variant_in_stock', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_display_price(self, obj):
        """Get display price (default variant price for variable products)"""
        return obj.get_display_price()
    
    def get_display_old_price(self, obj):
        """Get display old price (default variant old price for variable products)"""
        return obj.get_display_old_price()
    
    def get_default_variant_in_stock(self, obj):
        """Check if default variant is in stock"""
        return obj.is_default_variant_in_stock()

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for product create/update operations"""
    variants = serializers.ListField(required=False, write_only=True, allow_empty=True)
    options = serializers.ListField(required=False, write_only=True, allow_empty=True)
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
            'taxable', 'featured', 'tags', 'images', 'uploaded_images', 'variants', 'options'
        ]
    
    def validate_variants(self, value):
        """Validate variants data"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Variants must be a list")
        
        validated_variants = []
        for i, variant_data in enumerate(value):
            if not isinstance(variant_data, dict):
                raise serializers.ValidationError(f"Variant {i} must be a dictionary")
            
            # Validate required fields
            if 'title' not in variant_data or not variant_data['title']:
                raise serializers.ValidationError(f"Variant {i} must have a title")
            
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
                if not isinstance(dynamic_options, list):
                    raise serializers.ValidationError(f"Variant {i} dynamic_options must be a list")
                
                for j, option in enumerate(dynamic_options):
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
        
        return validated_variants
    
    def validate_options(self, value):
        """Validate options data"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Options must be a list")
        
        validated_options = []
        for i, option_data in enumerate(value):
            if not isinstance(option_data, dict):
                raise serializers.ValidationError(f"Option {i} must be a dictionary")
            
            # Validate required fields
            if 'name' not in option_data or not option_data['name']:
                raise serializers.ValidationError(f"Option {i} must have a name")
            
            if 'position' not in option_data:
                option_data['position'] = i + 1
            else:
                try:
                    option_data['position'] = int(option_data['position'])
                except (ValueError, TypeError):
                    option_data['position'] = i + 1
            
            validated_options.append(option_data)
        
        return validated_options

    def _generate_unique_sku(self, product, variant_data):
        """Generate a unique SKU for a variant"""
        from django.utils.text import slugify
        import time
        import random
        
        # Generate base SKU from product title
        base_sku = slugify(product.title)[:10].upper()
        print(f"Base SKU: {base_sku}")
        
        # Check if variant has option values
        option_parts = []
        if variant_data.get('option1_value'):
            option_parts.append(slugify(variant_data['option1_value'])[:3].upper())
        if variant_data.get('option2_value'):
            option_parts.append(slugify(variant_data['option2_value'])[:3].upper())
        if variant_data.get('option3_value'):
            option_parts.append(slugify(variant_data['option3_value'])[:3].upper())
        
        if option_parts:
            sku = f"{base_sku}-{'-'.join(option_parts)}"
            print(f"SKU with options: {sku}")
        else:
            # Generate unique SKU using microsecond timestamp and random number
            timestamp = str(int(time.time() * 1000000))[-8:]  # Last 8 digits of microsecond timestamp
            random_num = str(random.randint(1000, 9999))  # 4-digit random number
            sku = f"{base_sku}-{timestamp}{random_num}"
            print(f"SKU with timestamp: {sku}")
        
        # Ensure SKU is unique by checking database
        counter = 1
        original_sku = sku
        while ProductVariant.objects.filter(sku=sku).exists():
            sku = f"{original_sku}-{counter}"
            counter += 1
            print(f"SKU collision, trying: {sku}")
        
        print(f"Final SKU: {sku}")
        return sku

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        variants_data = validated_data.pop('variants', [])
        options_data = validated_data.pop('options', [])
        images_data = validated_data.pop('images', [])
        
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
            
            # Process options data
            if options_data:
                for i, option in enumerate(options_data):
                    # Set option names to product fields
                    if i == 0:
                        product.option1_name = option['name']
                    elif i == 1:
                        product.option2_name = option['name']
                    elif i == 2:
                        product.option3_name = option['name']
                product.save()
            
            # Set default variant for variable products
            if product.product_type == 'variable' and variants_data:
                # Set first variant as default
                if variants_data:
                    # Find the created variant and set as default
                    created_variants = product.variants.all()
                    if created_variants.exists():
                        default_variant = created_variants.first()
                        product.set_default_variant(default_variant)
            
            # Create variants with dynamic options
            for i, variant_data in enumerate(variants_data):
                print(f"Processing variant {i}: {variant_data}")
                dynamic_options_data = variant_data.pop('dynamic_options', [])
                print(f"Dynamic options for variant {i}: {dynamic_options_data}")
                
                try:
                    # Remove any None or empty string values for optional fields
                    # Also remove read-only fields that shouldn't be set during creation
                    read_only_fields = ['is_in_stock', 'display_price', 'discount_percentage', 'option_values', 'option_names', 'all_options', 'dynamic_options']
                    cleaned_variant_data = {}
                    for key, value in variant_data.items():
                        if key not in read_only_fields and value is not None and value != '':
                            cleaned_variant_data[key] = value
                    
                    print(f"Cleaned variant data: {cleaned_variant_data}")
                    
                    # Generate unique SKU before creating the variant
                    if 'sku' not in cleaned_variant_data or not cleaned_variant_data['sku']:
                        cleaned_variant_data['sku'] = self._generate_unique_sku(product, cleaned_variant_data)
                        print(f"Generated SKU: {cleaned_variant_data['sku']}")
                    
                    variant = ProductVariant.objects.create(product=product, **cleaned_variant_data)
                    print(f"Created variant {variant.id}")
                    
                    # Create dynamic options
                    if dynamic_options_data:
                        variant.set_dynamic_options(dynamic_options_data)
                except Exception as e:
                    print(f"Error creating variant {i}: {e}")
                    # Delete the product if variant creation fails
                    product.delete()
                    raise serializers.ValidationError(f"Error creating variant: {str(e)}")
            
            return product
            
        except Exception as e:
            raise serializers.ValidationError(f"Error creating product: {str(e)}")
    
    def is_valid(self, raise_exception=False):
        """Override is_valid to add more debugging"""
        is_valid = super().is_valid(raise_exception=False)
        if not is_valid:
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
                
                # Remove read-only fields that shouldn't be set during creation
                read_only_fields = ['is_in_stock', 'display_price', 'discount_percentage', 'option_values', 'option_names', 'all_options', 'dynamic_options']
                cleaned_variant_data = {}
                for key, value in variant_data.items():
                    if key not in read_only_fields and value is not None and value != '':
                        cleaned_variant_data[key] = value
                
                # Generate unique SKU before creating the variant
                if 'sku' not in cleaned_variant_data or not cleaned_variant_data['sku']:
                    cleaned_variant_data['sku'] = self._generate_unique_sku(instance, cleaned_variant_data)
                    print(f"Generated SKU for update: {cleaned_variant_data['sku']}")
                
                variant = ProductVariant.objects.create(product=instance, **cleaned_variant_data)
                
                # Create dynamic options
                if dynamic_options_data:
                    variant.set_dynamic_options(dynamic_options_data)
        
        return instance
