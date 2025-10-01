from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .role_management_serializers import AdminStaffUserSerializer, SetUserRoleSerializer, CreateAdminUserSerializer


User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_admins_and_staff(request):
    """Return only staff and/or superusers."""
    users = User.objects.select_related('profile').filter(is_staff=True) | User.objects.select_related('profile').filter(is_superuser=True)
    users = users.distinct().order_by('-date_joined')
    serializer = AdminStaffUserSerializer(users, many=True)
    return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def set_user_role(request, user_id):
    """Set is_staff / is_superuser for a target user. Only superusers can change roles."""
    if not request.user.is_superuser:
        return Response({'success': False, 'message': 'Only superusers can change user roles.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SetUserRoleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    if 'is_staff' in data:
        user.is_staff = data['is_staff']
    if 'is_superuser' in data:
        user.is_superuser = data['is_superuser']
    user.save(update_fields=['is_staff', 'is_superuser'])

    return Response({
        'success': True,
        'message': 'User role updated successfully',
        'data': AdminStaffUserSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_admin_user(request):
    """Create a new admin/staff user without email verification."""
    print('🔍 DEBUG: create_admin_user called')
    print('🔍 DEBUG: Request data:', request.data)
    print('🔍 DEBUG: User:', request.user.email, 'is_superuser:', request.user.is_superuser)
    
    if not request.user.is_superuser:
        return Response({'success': False, 'message': 'Only superusers can create admin users.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CreateAdminUserSerializer(data=request.data)
    print('🔍 DEBUG: Serializer data:', serializer.initial_data)
    print('🔍 DEBUG: Serializer is_valid:', serializer.is_valid())
    if not serializer.is_valid():
        print('🔍 DEBUG: Serializer errors:', serializer.errors)
    
    if serializer.is_valid():
        # Create user with admin privileges
        user = User.objects.create(
            email=serializer.validated_data['email'],
            password=make_password(serializer.validated_data['password']),
            is_staff=serializer.validated_data.get('is_staff', False),
            is_superuser=serializer.validated_data.get('is_superuser', False),
            is_active=True,  # Auto-activate admin users
            is_email_verified=True  # Skip email verification for admin-created users
        )
        
        # Update profile if full_name provided
        if serializer.validated_data.get('full_name'):
            user.profile.full_name = serializer.validated_data['full_name']
            user.profile.save()
        
        print('🔍 DEBUG: User created successfully:', user.email)
        return Response({
            'success': True,
            'message': 'Admin user created successfully',
            'data': AdminStaffUserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    print('🔍 DEBUG: Validation failed, returning 400')
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def check_email_exists(request):
    """Check if email already exists in the system."""
    email = request.data.get('email')
    if not email:
        return Response({'success': False, 'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects.filter(email__iexact=email).exists()
    return Response({
        'success': True,
        'exists': exists,
        'message': 'Email already exists' if exists else 'Email is available'
    }, status=status.HTTP_200_OK)


