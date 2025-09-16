"""
Cart Serializers
================

This module contains DRF serializers for cart functionality.
Handles serialization of cart data for API responses and requests.

Serializers:
- CartSerializer: Full cart data with items
- CartItemSerializer: Individual cart item data
- AddToCartSerializer: For adding items to cart
"""

from rest_framework import serializers
from cart.models import Cart, CartItem
from products.serializers import ProductListSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Cart Item Serializer
    ====================
    
    Serializes individual cart items with product and variant details.
    Includes calculated fields for pricing and availability.
    """
    
    # Product and variant details
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    
    # Calculated fields
    current_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    can_increase = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'variant',
            'quantity',
            'unit_price',
            'current_price',
            'total_price',
            'is_available',
            'can_increase',
            'added_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'unit_price',
            'added_at',
            'updated_at'
        ]
    
    def get_current_price(self, obj):
        """Get current price of the product/variant"""
        return obj.get_current_price()
    
    def get_total_price(self, obj):
        """Get total price for this cart item"""
        return obj.get_total_price()
    
    def get_is_available(self, obj):
        """Check if item is still available"""
        return obj.is_available()
    
    def get_can_increase(self, obj):
        """Check if quantity can be increased"""
        return obj.can_increase_quantity()


class AddToCartSerializer(serializers.Serializer):
    """
    Add to Cart Serializer
    ======================
    
    Handles adding items to cart with validation.
    Supports both simple products and products with variants.
    """
    
    # Required fields
    product_id = serializers.IntegerField(
        help_text="ID of the product to add to cart"
    )
    
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=1,
        help_text="Quantity to add (1-100)"
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
        quantity = attrs.get('quantity')
        
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
            
            # Check variant availability
            if variant.quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {variant.quantity} items available in this variant"
                )
        else:
            # Check product availability
            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {product.quantity} items available"
                )
        
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """
    Cart Serializer
    ===============
    
    Serializes complete cart data including all items.
    Includes calculated totals and metadata.
    """
    
    # Related items
    items = CartItemSerializer(many=True, read_only=True)
    
    # Calculated fields
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'session_key',
            'items',
            'total_items',
            'subtotal',
            'is_expired',
            'created_at',
            'updated_at',
            'expires_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'session_key',
            'total_items',
            'subtotal',
            'created_at',
            'updated_at',
            'expires_at'
        ]
    
    def get_total_items(self, obj):
        """Get total number of items in cart"""
        # Calculate total items from cart items
        total_items = sum(item.quantity for item in obj.items.all())
        return total_items
    
    def get_subtotal(self, obj):
        """Get cart subtotal"""
        # Calculate subtotal from cart items
        subtotal = sum(item.get_total_price() for item in obj.items.all())
        return float(subtotal)
    
    def get_is_expired(self, obj):
        """Check if cart has expired"""
        return obj.is_expired()


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Update Cart Item Serializer
    ============================
    
    Handles updating cart item quantities.
    """
    
    action = serializers.ChoiceField(
        choices=['increase', 'decrease', 'set'],
        help_text="Action to perform: increase, decrease, or set quantity"
    )
    
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        help_text="Quantity to set (required for 'set' action)"
    )
    
    def validate(self, attrs):
        """Validate action and quantity"""
        action = attrs.get('action')
        quantity = attrs.get('quantity')
        
        if action == 'set' and quantity is None:
            raise serializers.ValidationError(
                "Quantity is required for 'set' action"
            )
        
        return attrs
