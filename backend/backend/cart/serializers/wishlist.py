"""
Wishlist Serializers
====================

This module contains DRF serializers for wishlist functionality.
Handles serialization of wishlist data for API responses and requests.

Serializers:
- WishlistSerializer: Full wishlist data with items
- WishlistItemSerializer: Individual wishlist item data
"""

from rest_framework import serializers
from cart.models import Wishlist, WishlistItem
from products.serializers import ProductListSerializer, ProductVariantSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Wishlist Item Serializer
    =========================
    
    Serializes individual wishlist items with product and variant details.
    Includes calculated fields for pricing and availability.
    """
    
    # Product and variant details
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    
    # Calculated fields
    current_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = WishlistItem
        fields = [
            'id',
            'product',
            'variant',
            'current_price',
            'is_available',
            'added_at'
        ]
        read_only_fields = [
            'id',
            'added_at'
        ]
    
    def get_current_price(self, obj):
        """Get current price of the product/variant"""
        return obj.get_current_price()
    
    def get_is_available(self, obj):
        """Check if item is still available"""
        return obj.is_available()


class WishlistSerializer(serializers.ModelSerializer):
    """
    Wishlist Serializer
    ====================
    
    Serializes complete wishlist data including all items.
    Includes calculated totals and metadata.
    """
    
    # Related items
    items = WishlistItemSerializer(many=True, read_only=True)
    
    # Calculated fields
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id',
            'user',
            'name',
            'items',
            'total_items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'total_items',
            'created_at',
            'updated_at'
        ]
    
    def get_total_items(self, obj):
        """Get total number of items in wishlist"""
        return obj.get_total_items()


class AddToWishlistSerializer(serializers.Serializer):
    """
    Add to Wishlist Serializer
    ===========================
    
    Handles adding items to wishlist with validation.
    Supports both simple products and products with variants.
    """
    
    # Required fields
    product_id = serializers.IntegerField(
        help_text="ID of the product to add to wishlist"
    )
    
    # Optional variant support
    variant_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID of the product variant (optional)"
    )
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        from products.models import Product
        
        try:
            product = Product.objects.get(id=value, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")
        
        return value
    
    def validate_variant_id(self, value):
        """Validate variant exists and belongs to the product"""
        if value is None:
            return value
        
        from products.models import ProductVariant
        
        try:
            variant = ProductVariant.objects.get(id=value)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("Product variant not found")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')
        
        # Get product and variant
        from products.models import Product, ProductVariant
        
        product = Product.objects.get(id=product_id)
        
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
            
            # Check if variant belongs to product
            if variant.product != product:
                raise serializers.ValidationError(
                    "Variant does not belong to the specified product"
                )
        
        return attrs
