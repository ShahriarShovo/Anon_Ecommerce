from rest_framework import serializers
from .footer_settings_model import FooterSettings, SocialMediaLink

class SocialMediaLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for social media links
    """
    class Meta:
        model = SocialMediaLink
        fields = [
            'id', 'platform', 'url', 'icon', 'is_active', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SocialMediaLinkCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating social media links
    """
    class Meta:
        model = SocialMediaLink
        fields = ['platform', 'url', 'icon', 'is_active', 'order']

class FooterSettingsSerializer(serializers.ModelSerializer):
    """
    Main footer settings serializer
    """
    social_links = SocialMediaLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = FooterSettings
        fields = [
            'id', 'description', 'copyright', 'email', 'phone', 'about_us',
            'mission', 'vision', 'business_hours', 'quick_response', 'is_active', 'social_links', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class FooterSettingsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating footer settings
    """
    social_links = SocialMediaLinkCreateSerializer(many=True, required=False)
    
    class Meta:
        model = FooterSettings
        fields = [
            'description', 'copyright', 'email', 'phone', 'about_us',
            'mission', 'vision', 'business_hours', 'quick_response', 'is_active', 'social_links'
        ]

    def create(self, validated_data):
        social_links_data = validated_data.pop('social_links', [])
        footer_setting = FooterSettings.objects.create(**validated_data)
        
        # Create social media links
        for link_data in social_links_data:
            SocialMediaLink.objects.create(
                footer_setting=footer_setting,
                **link_data
            )
        
        return footer_setting

    def update(self, instance, validated_data):
        social_links_data = validated_data.pop('social_links', None)
        
        # Update footer setting fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update social media links if provided
        if social_links_data is not None:
            # Delete existing social links
            instance.social_links.all().delete()
            
            # Create new social links
            for link_data in social_links_data:
                SocialMediaLink.objects.create(
                    footer_setting=instance,
                    **link_data
                )
        
        return instance

class FooterSettingsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing footer settings
    """
    social_links_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FooterSettings
        fields = [
            'id', 'description', 'copyright', 'email', 'phone', 'about_us',
            'is_active', 'social_links_count', 'created_at', 'updated_at'
        ]
    
    def get_social_links_count(self, obj):
        return obj.social_links.filter(is_active=True).count()
