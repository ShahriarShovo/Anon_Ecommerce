from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models.notifications.discount import Discount, DiscountUsage
from products.models import Product, Category

User = get_user_model()


class DiscountSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    is_valid = serializers.SerializerMethodField()
    target_products_count = serializers.SerializerMethodField()
    target_categories_count = serializers.SerializerMethodField()
    remaining_usage = serializers.SerializerMethodField()
    target_products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    target_categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Discount
        fields = [
            'id', 'name', 'discount_type', 'status', 'percentage', 'minimum_amount',
            'maximum_discount_amount', 'minimum_quantity', 'valid_from', 'valid_until',
            'target_products', 'target_categories', 'usage_limit', 'usage_count',
            'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at',
            'show_in_notifications', 'notification_message', 'is_valid', 'target_products_count',
            'target_categories_count', 'remaining_usage', 'display_type', 'discount_image',
            'image_alt_text', 'modal_title', 'modal_button_text'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'usage_count']
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_target_products_count(self, obj):
        return obj.target_products.count()
    
    def get_target_categories_count(self, obj):
        return obj.target_categories.count()
    
    def get_remaining_usage(self, obj):
        if obj.usage_limit:
            return max(0, obj.usage_limit - obj.usage_count)
        return None


class DiscountCreateSerializer(serializers.ModelSerializer):
    target_products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), required=False)
    target_categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), required=False)
    discount_image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Discount
        fields = [
            'name', 'discount_type', 'percentage', 'minimum_amount', 'maximum_discount_amount',
            'minimum_quantity', 'valid_from', 'valid_until', 'target_products', 'target_categories',
            'usage_limit', 'show_in_notifications', 'notification_message', 'status', 'display_type',
            'discount_image', 'image_alt_text', 'modal_title', 'modal_button_text'
        ]
    
    def validate(self, data):
        # Validate percentage
        percentage = data.get('percentage', 0)
        if percentage <= 0 or percentage > 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100")
        
        # Validate time range
        valid_from = data.get('valid_from')
        valid_until = data.get('valid_until')
        if valid_until and valid_from and valid_until <= valid_from:
            raise serializers.ValidationError("Valid until must be after valid from")
        
        # Validate discount type specific requirements
        discount_type = data.get('discount_type')
        target_products = data.get('target_products', [])
        target_categories = data.get('target_categories', [])
        
        if discount_type == 'product_specific' and not target_products:
            raise serializers.ValidationError("Target products must be specified for product-specific discounts")
        
        if discount_type == 'category' and not target_categories:
            raise serializers.ValidationError("Target categories must be specified for category discounts")
        
        return data


class DiscountUsageSerializer(serializers.ModelSerializer):
    discount_name = serializers.CharField(source='discount.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = DiscountUsage
        fields = [
            'id', 'discount', 'discount_name', 'user', 'user_email', 'session_key',
            'order', 'discount_amount', 'used_at', 'ip_address'
        ]
        read_only_fields = ['used_at']


class DiscountCalculationSerializer(serializers.Serializer):
    """Serializer for discount calculation requests"""
    cart_items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of cart items with product_id, quantity, and price"
    )
    user_id = serializers.IntegerField(required=False, allow_null=True)
    session_key = serializers.CharField(required=False)


class DiscountStatsSerializer(serializers.Serializer):
    total_discounts = serializers.IntegerField()
    active_discounts = serializers.IntegerField()
    total_usage = serializers.IntegerField()
    total_discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    discounts_by_type = serializers.DictField()
    recent_discounts = serializers.ListField(child=serializers.DictField(), required=False)
