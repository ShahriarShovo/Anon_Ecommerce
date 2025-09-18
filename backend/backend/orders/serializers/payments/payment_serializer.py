from rest_framework import serializers
from orders.models.payments.payment import Payment
from orders.models.payments.payment_method import PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'name',
            'method_type',
            'description',
            'is_active',
            'is_cod',
            'processing_fee',
            'processing_fee_type',
            'display_order',
            'icon'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    
    payment_method = PaymentMethodSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_display = serializers.CharField(source='get_amount_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'payment_method',
            'amount',
            'amount_display',
            'status',
            'status_display',
            'transaction_id',
            'gateway_response',
            'cod_collected',
            'cod_collected_at',
            'cod_collected_by',
            'created_at',
            'updated_at',
            'completed_at'
        ]
        read_only_fields = [
            'id', 'order', 'created_at', 'updated_at', 'completed_at'
        ]
