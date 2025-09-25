from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models.notifications.notification import Notification, NotificationView

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    target_users_count = serializers.SerializerMethodField()
    is_visible = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'target_type',
            'target_users', 'is_active', 'show_until', 'priority',
            'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at',
            'total_views', 'unique_views', 'target_users_count', 'is_visible'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'total_views', 'unique_views']
    
    def get_target_users_count(self, obj):
        return obj.target_users.count()
    
    def get_is_visible(self, obj):
        return obj.is_visible()


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'target_type',
            'target_users', 'is_active', 'show_until', 'priority'
        ]
    
    def validate(self, data):
        target_type = data.get('target_type')
        target_users = data.get('target_users', [])
        
        if target_type == 'specific' and not target_users:
            raise serializers.ValidationError("Target users must be specified when target_type is 'specific'")
        
        return data


class NotificationViewSerializer(serializers.ModelSerializer):
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = NotificationView
        fields = [
            'id', 'notification', 'notification_title', 'session_key', 'user', 'user_email',
            'viewed_at', 'ip_address'
        ]
        read_only_fields = ['viewed_at']


class NotificationStatsSerializer(serializers.Serializer):
    total_notifications = serializers.IntegerField()
    active_notifications = serializers.IntegerField()
    total_views = serializers.IntegerField()
    unique_views = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = NotificationSerializer(many=True)
