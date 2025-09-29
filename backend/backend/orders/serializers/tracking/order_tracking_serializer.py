from rest_framework import serializers
from ...models.orders.order import Order
from ...models.orders.order_item import OrderItem
from ...models.orders.address import Address
from ...models.payments.payment import Payment


class OrderItemTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for order items in tracking response
    """
    product_image = serializers.SerializerMethodField()
    variation = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_sku', 'variant_title',
            'quantity', 'unit_price', 'total_price', 'product_image', 'variation'
        ]
    
    def get_product_image(self, obj):
        """Get product image URL"""
        try:
            if obj.product:
                # Try to get primary image first
                primary_image = obj.product.primary_image
                if primary_image and primary_image.image:
                    image_url = primary_image.image.url
                    # Convert relative URL to absolute URL
                    if image_url.startswith('/media/'):
                        image_url = f"http://localhost:8000{image_url}"
                    print(f"Product {obj.product.id} primary image URL: {image_url}")
                    return image_url
                
                # Fallback to first image
                if obj.product.images.exists():
                    first_image = obj.product.images.first()
                    if first_image and first_image.image:
                        image_url = first_image.image.url
                        # Convert relative URL to absolute URL
                        if image_url.startswith('/media/'):
                            image_url = f"http://localhost:8000{image_url}"
                        print(f"Product {obj.product.id} first image URL: {image_url}")
                        return image_url
                
                print(f"Product {obj.product.id} has no images")
            else:
                print("No product found for order item")
            return None
        except Exception as e:
            print(f"Error getting product image for {obj.product.id if obj.product else 'None'}: {str(e)}")
            return None
    
    def get_variation(self, obj):
        """Get product variation details"""
        if obj.variant_title:
            return obj.variant_title
        return None


class AddressTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for delivery address in tracking response
    """
    class Meta:
        model = Address
        fields = [
            'full_name', 'address_line_1', 'address_line_2',
            'city', 'postal_code', 'country', 'phone_number'
        ]


class PaymentTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for payment information in tracking response
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    amount_display = serializers.CharField(source='get_amount_display', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    payment_method_type = serializers.CharField(source='payment_method.method_type', read_only=True)
    is_cod = serializers.BooleanField(source='is_cash_on_delivery', read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'amount_display', 'status', 'status_display', 'status_color',
            'payment_method_name', 'payment_method_type', 'is_cod',
            'transaction_id', 'cod_collected', 'cod_collected_at', 'cod_collected_by',
            'completed_at', 'created_at', 'updated_at', 'can_be_refunded'
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for order tracking response
    """
    items = OrderItemTrackingSerializer(many=True, read_only=True)
    shipping_address = AddressTrackingSerializer(source='delivery_address', read_only=True)
    payment = PaymentTrackingSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount_display = serializers.CharField(source='get_total_amount_display', read_only=True)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    tracking_number = serializers.SerializerMethodField()
    carrier = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'status_color',
            'subtotal', 'shipping_cost', 'tax_amount', 'total_amount', 'total_amount_display',
            'notes', 'created_at', 'updated_at', 'estimated_delivery', 'delivered_at',
            'shipping_address', 'payment', 'items', 'can_be_cancelled', 'can_be_refunded',
            'tracking_number', 'carrier'
        ]
    
    def get_tracking_number(self, obj):
        """Get tracking number if available"""
        # This would be implemented based on your tracking system
        # For now, return order number as tracking number
        return obj.order_number
    
    def get_carrier(self, obj):
        """Get carrier information if available"""
        # This would be implemented based on your shipping system
        # For now, return default carrier
        if obj.status in ['shipped', 'delivered']:
            return "GreatKart Logistics"
        return None


class OrderTrackingRequestSerializer(serializers.Serializer):
    """
    Serializer for order tracking request
    """
    tracking_number = serializers.CharField(
        max_length=50,
        help_text="Order tracking number"
    )
    
    def validate_tracking_number(self, value):
        """Validate tracking number format"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Tracking number must be at least 3 characters long.")
        return value.strip().upper()
