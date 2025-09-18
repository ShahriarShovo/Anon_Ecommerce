from rest_framework import serializers
from orders.models.orders.order import Order
from orders.models.orders.order_item import OrderItem
from orders.serializers.orders.address_serializer import AddressSerializer
from orders.serializers.orders.order_item_serializer import OrderItemSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    
    delivery_address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount_display = serializers.CharField(source='get_total_amount_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'status',
            'status_display',
            'delivery_address',
            'subtotal',
            'shipping_cost',
            'tax_amount',
            'total_amount',
            'total_amount_display',
            'notes',
            'items',
            'created_at',
            'updated_at',
            'estimated_delivery',
            'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'created_at', 'updated_at',
            'delivered_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    
    class Meta:
        model = Order
        fields = [
            'delivery_address',
            'notes',
            'subtotal',
            'shipping_cost',
            'tax_amount',
            'total_amount'
        ]
    
    def create(self, validated_data):
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
