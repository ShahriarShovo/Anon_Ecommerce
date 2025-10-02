from rest_framework import serializers
from orders.models.orders.address import Address

class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'full_name',
            'phone_number',
            'city',
            'address_line_1',
            'address_line_2',
            'postal_code',
            'country',
            'is_default',
            'address_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating addresses from order form"""
    
    class Meta:
        model = Address
        fields = [
            'full_name',
            'phone_number',
            'city',
            'address_line_1',
            'address_line_2',
            'postal_code',
            'country',
            'address_type'
        ]
    
    def create(self, validated_data):
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        validated_data['is_default'] = True  # Set as default for new orders
        return super().create(validated_data)
