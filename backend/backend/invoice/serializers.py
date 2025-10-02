from rest_framework import serializers
from invoice.models import Invoice
from orders.serializers.orders.order_serializer import OrderSerializer

class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    
    order = OrderSerializer(read_only=True)
    invoice_date_display = serializers.CharField(source='get_invoice_date_display', read_only=True)
    due_date_display = serializers.CharField(source='get_due_date_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'order',
            'status',
            'invoice_date',
            'invoice_date_display',
            'due_date',
            'due_date_display',
            'company_name',
            'company_logo',
            'company_address',
            'company_phone',
            'company_email',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at'
        ]
