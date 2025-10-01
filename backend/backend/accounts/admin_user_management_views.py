from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Profile
from .serializers import UserListSerializer, ProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class AdminUserProfileUpdateView(generics.UpdateAPIView):
    """
    Admin can update any user's profile
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['patch']

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return User.objects.get(id=user_id)

    def perform_update(self, serializer):
        user = self.get_object()
        
        # Update user basic info
        serializer.save()
        
        # Update profile if provided
        profile_data = self.request.data.get('profile', {})
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=user)
            profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Admin can change any user's password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password'),
        },
        required=['user_id', 'new_password', 'confirm_password']
    ),
    responses={
        200: openapi.Response(description="Password changed successfully"),
        400: openapi.Response(description="Bad request - validation error"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def admin_change_user_password(request):
    """
    Admin can change any user's password
    """
    try:
        user_id = request.data.get('user_id')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not user_id or not new_password or not confirm_password:
            return Response({
                'success': False,
                'message': 'user_id, new_password, and confirm_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': f'Password updated successfully for {user.email}'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error updating password: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Get user details for admin management",
    responses={
        200: openapi.Response(description="User details retrieved successfully"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def admin_get_user_details(request, user_id):
    """
    Admin can get detailed user information
    """
    try:
        user = User.objects.select_related('profile').get(id=user_id)
        
        user_data = {
            'id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_email_verified': user.is_email_verified,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'profile': {
                'full_name': user.profile.full_name if hasattr(user, 'profile') else '',
                'username': user.profile.username if hasattr(user, 'profile') else '',
                'phone': user.profile.phone if hasattr(user, 'profile') else '',
                'address': user.profile.address if hasattr(user, 'profile') else '',
            } if hasattr(user, 'profile') else {}
        }
        
        return Response({
            'success': True,
            'data': user_data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving user details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
