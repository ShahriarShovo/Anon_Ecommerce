from rest_framework import serializers
from ...models.contact.contact import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model
    """
    status = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'email', 'subject', 'message', 
            'is_read', 'is_replied', 'status', 'is_new',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_read', 'is_replied', 'created_at', 'updated_at']


class ContactCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact messages
    """
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
    
    def validate_name(self, value):
        """Validate name field"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_subject(self, value):
        """Validate subject field"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long.")
        return value.strip()
    
    def validate_message(self, value):
        """Validate message field"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()


class ContactUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating contact messages (admin use)
    """
    class Meta:
        model = Contact
        fields = ['is_read', 'is_replied']
    
    def update(self, instance, validated_data):
        """Update contact message status"""
        instance.is_read = validated_data.get('is_read', instance.is_read)
        instance.is_replied = validated_data.get('is_replied', instance.is_replied)
        instance.save()
        return instance
