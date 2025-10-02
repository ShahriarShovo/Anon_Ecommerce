from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models import Conversation, Message

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    """Full conversation serializer with all details"""
    customer_name = serializers.CharField(source='customer.profile.full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to.email', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'assigned_to', 'assigned_to_name', 'assigned_to_email',
            'status', 'created_at', 'updated_at', 'last_message_at',
            'unread_user_count', 'unread_staff_count', 'unread_count',
            'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender': last_message.sender.email,
                'created_at': last_message.created_at,
                'message_type': last_message.message_type
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread count based on user type"""
        request = self.context.get('request')
        if request and request.user:
            if request.user.is_staff or request.user.is_superuser:
                return obj.unread_staff_count
            else:
                return obj.unread_user_count
        return 0

class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified conversation serializer for list views"""
    customer_name = serializers.CharField(source='customer.profile.full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'assigned_to', 'assigned_to_name', 'status', 
            'created_at', 'last_message_at', 'unread_count',
            'last_message_preview'
        ]
    
    def get_last_message_preview(self, obj):
        """Get preview of last message"""
        last_message = obj.messages.last()
        if last_message:
            content = last_message.content
            if len(content) > 50:
                content = content[:50] + '...'
            return {
                'content': content,
                'sender': last_message.sender.email,
                'created_at': last_message.created_at,
                'message_type': last_message.message_type
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread count based on user type"""
        request = self.context.get('request')
        if request and request.user:
            if request.user.is_staff or request.user.is_superuser:
                return obj.unread_staff_count
            else:
                return obj.unread_user_count
        return 0

class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations"""
    
    class Meta:
        model = Conversation
        fields = ['id', 'assigned_to', 'status']
    
    def create(self, validated_data):
        """Create conversation and add customer as participant"""
        # Set customer from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['customer'] = request.user
        
        conversation = super().create(validated_data)
        
        # Add customer as participant
        from ...models import Participant
        Participant.objects.create(
            conversation=conversation,
            user=conversation.customer
        )
        
        return conversation

class ConversationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating conversations"""
    
    class Meta:
        model = Conversation
        fields = ['assigned_to', 'status']
    
    def update(self, instance, validated_data):
        """Update conversation and handle participant changes"""
        assigned_to = validated_data.get('assigned_to')
        
        if assigned_to and assigned_to != instance.assigned_to:
            # Add new assigned user as participant if not already
            from ...models import Participant
            Participant.objects.get_or_create(
                conversation=instance,
                user=assigned_to
            )
        
        return super().update(instance, validated_data)
