from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .footer_settings_model import FooterSettings, SocialMediaLink
from .footer_settings_serializers import (
    FooterSettingsSerializer, 
    FooterSettingsCreateSerializer,
    FooterSettingsListSerializer,
    SocialMediaLinkSerializer
)

class FooterSettingsListCreateView(generics.ListCreateAPIView):
    """
    List all footer settings or create a new one
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FooterSettingsCreateSerializer
        return FooterSettingsListSerializer
    
    def get_queryset(self):
        return FooterSettings.objects.all().order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            footer_setting = serializer.save()
            response_serializer = FooterSettingsSerializer(footer_setting)
            return Response({
                'success': True,
                'message': 'Footer settings created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to create footer settings',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class FooterSettingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a footer setting
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = FooterSettingsSerializer
    
    def get_queryset(self):
        return FooterSettings.objects.all()
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = FooterSettingsCreateSerializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            footer_setting = serializer.save()
            response_serializer = FooterSettingsSerializer(footer_setting)
            return Response({
                'success': True,
                'message': 'Footer settings updated successfully',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Failed to update footer settings',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Footer settings deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

class SocialMediaLinkListCreateView(generics.ListCreateAPIView):
    """
    List social media links for a footer setting or create new ones
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SocialMediaLinkSerializer
    
    def get_queryset(self):
        footer_setting_id = self.kwargs.get('footer_setting_id')
        return SocialMediaLink.objects.filter(
            footer_setting_id=footer_setting_id
        ).order_by('order', 'platform')
    
    def create(self, request, *args, **kwargs):
        footer_setting_id = self.kwargs.get('footer_setting_id')
        footer_setting = get_object_or_404(FooterSettings, id=footer_setting_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(footer_setting=footer_setting)
            return Response({
                'success': True,
                'message': 'Social media link created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to create social media link',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SocialMediaLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a social media link
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SocialMediaLinkSerializer
    
    def get_queryset(self):
        footer_setting_id = self.kwargs.get('footer_setting_id')
        return SocialMediaLink.objects.filter(footer_setting_id=footer_setting_id)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_footer_settings(request):
    """
    Get active footer settings for public display
    """
    try:
        footer_setting = FooterSettings.objects.filter(is_active=True).first()
        
        if not footer_setting:
            # Return default values if no active footer setting
            return Response({
                'success': True,
                'data': {
                    'description': 'One of the biggest online shopping platform in Bangladesh.',
                    'copyright': '© 2024 GreatKart. All rights reserved',
                    'email': 'info@greatkart.com',
                    'phone': '+880-123-456-789',
                    'about_us': 'GreatKart is your one-stop destination for quality products at affordable prices.',
                    'social_links': []
                }
            }, status=status.HTTP_200_OK)
        
        serializer = FooterSettingsSerializer(footer_setting)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to fetch footer settings',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_update_social_links(request, footer_setting_id):
    """
    Bulk update social media links for a footer setting
    """
    try:
        footer_setting = get_object_or_404(FooterSettings, id=footer_setting_id)
        social_links_data = request.data.get('social_links', [])
        
        # Delete existing social links
        footer_setting.social_links.all().delete()
        
        # Create new social links
        created_links = []
        for link_data in social_links_data:
            social_link = SocialMediaLink.objects.create(
                footer_setting=footer_setting,
                platform=link_data.get('platform', ''),
                url=link_data.get('url', ''),
                icon=link_data.get('icon', 'fab fa-link'),
                is_active=link_data.get('is_active', True),
                order=link_data.get('order', 0)
            )
            created_links.append(social_link)
        
        serializer = SocialMediaLinkSerializer(created_links, many=True)
        return Response({
            'success': True,
            'message': f'{len(created_links)} social media links updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to update social media links',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
