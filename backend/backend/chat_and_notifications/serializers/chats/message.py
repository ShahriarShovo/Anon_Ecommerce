from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models import Message, Conversation

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """Full message serializer with sender details"""
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    is_sender_staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'sender_email',
            'message_type', 'content', 'attachments', 'created_at', 'updated_at',
            'delivery_status', 'is_read_by_recipient', 'read_at', 'is_sender_staff'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at', 'read_at']
    
    def get_is_sender_staff(self, obj):
        """Check if sender is staff/admin"""
        return obj.sender.is_staff or obj.sender.is_superuser


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    
    class Meta:
        model = Message
        fields = ['conversation', 'message_type', 'content', 'attachments']
    
    def create(self, validated_data):
        """Create message and set sender from request user"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['sender'] = request.user
        
        message = super().create(validated_data)
        return message
    
    def validate_conversation(self, value):
        """Validate that user has access to this conversation"""
        request = self.context.get('request')
        if request and request.user:
            # Check if user is customer or assigned staff
            if value.customer != request.user and value.assigned_to != request.user:
                if not (request.user.is_staff or request.user.is_superuser):
                    raise serializers.ValidationError("You don't have access to this conversation.")
        return value
    
    def validate_content(self, value):
        """Validate message content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        
        if len(value) > 1000:
            raise serializers.ValidationError("Message content is too long (max 1000 characters).")
        
        return value.strip()


class MessageListSerializer(serializers.ModelSerializer):
    """Simplified message serializer for list views"""
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    is_sender_staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'message_type', 'content',
            'created_at', 'delivery_status', 'is_read_by_recipient', 'is_sender_staff'
        ]
    
    def get_is_sender_staff(self, obj):
        """Check if sender is staff/admin"""
        return obj.sender.is_staff or obj.sender.is_superuser


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating messages (mark as read, etc.)"""
    
    class Meta:
        model = Message
        fields = ['delivery_status', 'is_read_by_recipient']
        read_only_fields = ['delivery_status']
    
    def update(self, instance, validated_data):
        """Update message status"""
        if validated_data.get('is_read_by_recipient'):
            instance.mark_as_read()
        return instance


class MessageMarkReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read"""
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        max_length=100,
        required=False
    )
    conversation_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """Validate that either message_ids or conversation_id is provided"""
        if not data.get('message_ids') and not data.get('conversation_id'):
            raise serializers.ValidationError("Either message_ids or conversation_id is required.")
        return data
    
    def validate_message_ids(self, value):
        """Validate message IDs"""
        if value and len(value) > 100:
            raise serializers.ValidationError("Too many message IDs (max 100).")
        return value
