from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models import Participant

User = get_user_model()


class ParticipantSerializer(serializers.ModelSerializer):
    """Serializer for conversation participants"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Participant
        fields = [
            'id', 'conversation', 'user', 'user_name', 'user_email',
            'joined_at', 'last_seen_at', 'is_online', 'is_active', 'is_staff'
        ]
        read_only_fields = ['id', 'joined_at', 'last_seen_at']
    
    def get_is_staff(self, obj):
        """Check if user is staff/admin"""
        return obj.user.is_staff or obj.user.is_superuser


class ParticipantCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding participants to conversations"""
    
    class Meta:
        model = Participant
        fields = ['conversation', 'user']
    
    def create(self, validated_data):
        """Create participant"""
        participant, created = Participant.objects.get_or_create(
            conversation=validated_data['conversation'],
            user=validated_data['user'],
            defaults={'is_active': True}
        )
        return participant


class ParticipantUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating participant status"""
    
    class Meta:
        model = Participant
        fields = ['is_online', 'is_active']
    
    def update(self, instance, validated_data):
        """Update participant status"""
        if 'is_online' in validated_data:
            instance.set_online_status(validated_data['is_online'])
        
        if 'is_active' in validated_data and not validated_data['is_active']:
            instance.deactivate()
        
        return instance


class OnlineStatusSerializer(serializers.Serializer):
    """Serializer for updating online status"""
    is_online = serializers.BooleanField()
    
    def update(self, instance, validated_data):
        """Update online status"""
        instance.set_online_status(validated_data['is_online'])
        return instance
