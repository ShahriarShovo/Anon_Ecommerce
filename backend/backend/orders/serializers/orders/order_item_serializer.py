from rest_framework import serializers
from orders.models.orders.order_item import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    
    product_name = serializers.CharField(read_only=True)
    variant_title = serializers.CharField(read_only=True)
    unit_price_display = serializers.CharField(source='get_unit_price_display', read_only=True)
    total_price_display = serializers.CharField(source='get_total_price_display', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'variant',
            'quantity',
            'unit_price',
            'unit_price_display',
            'total_price',
            'total_price_display',
            'product_name',
            'product_sku',
            'variant_title',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'order', 'created_at', 'updated_at',
            'product_name', 'product_sku', 'variant_title'
        ]
