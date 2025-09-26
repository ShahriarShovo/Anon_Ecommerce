from rest_framework import serializers
from ..models.notifications.logo import Logo


class LogoSerializer(serializers.ModelSerializer):
    """Serializer for Logo model"""
    logo_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Logo
        fields = [
            'id', 'name', 'logo_image', 'logo_url', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Logo"""
    
    class Meta:
        model = Logo
        fields = ['name', 'logo_image', 'is_active']
    
    def create(self, validated_data):
        # When creating a new logo, deactivate all other logos
        Logo.objects.filter(is_active=True).update(is_active=False)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # When updating to active, deactivate all other logos
        if validated_data.get('is_active', False):
            Logo.objects.filter(is_active=True).exclude(id=instance.id).update(is_active=False)
        return super().update(instance, validated_data)


class ActiveLogoSerializer(serializers.ModelSerializer):
    """Serializer for getting active logo (public endpoint)"""
    logo_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Logo
        fields = ['id', 'name', 'logo_url', 'created_at']
