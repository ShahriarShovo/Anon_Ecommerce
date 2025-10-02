from rest_framework import serializers
from .models import Logo, Banner

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

class BannerSerializer(serializers.ModelSerializer):
    """Serializer for Banner model"""
    banner_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Banner
        fields = [
            'id', 'name', 'banner_image', 'banner_url', 'is_active', 
            'display_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class BannerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Banner"""
    
    class Meta:
        model = Banner
        fields = ['name', 'banner_image', 'is_active', 'display_order']
    
    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ActiveBannerSerializer(serializers.ModelSerializer):
    """Serializer for getting active banners (public endpoint)"""
    banner_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Banner
        fields = ['id', 'name', 'banner_url', 'display_order', 'created_at']
