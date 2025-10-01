from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .permission_models import Permission, UserPermission, RolePermission, Role
from .serializers import PermissionSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_dynamic_permission(request):
    """
    Check if current user has a specific permission by codename
    """
    permission_codename = request.data.get('permission_codename')
    
    if not permission_codename:
        return Response({
            'error': 'Permission codename is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Superuser has all permissions
    if user.is_superuser:
        return Response({
            'has_permission': True,
            'permission_codename': permission_codename,
            'user_id': user.id,
            'is_superuser': True
        })
    
    try:
        # Check if permission exists
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
        
        # Check if user has direct permission
        has_direct_permission = UserPermission.objects.filter(
            user=user,
            permission=permission,
            is_active=True
        ).exists()
        
        # Check if user has permission through roles
        has_role_permission = RolePermission.objects.filter(
            role__user_roles__user=user,
            permission=permission,
            is_active=True
        ).exists()
        
        has_permission = has_direct_permission or has_role_permission
        
        return Response({
            'has_permission': has_permission,
            'permission_codename': permission_codename,
            'permission_name': permission.name,
            'user_id': user.id,
            'direct_permission': has_direct_permission,
            'role_permission': has_role_permission
        })
        
    except Permission.DoesNotExist:
        return Response({
            'has_permission': False,
            'permission_codename': permission_codename,
            'error': 'Permission does not exist',
            'user_id': user.id
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dynamic_permission(request):
    """
    Create a new permission dynamically
    """
    if not request.user.is_superuser:
        return Response({
            'error': 'Only superusers can create permissions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    name = request.data.get('name')
    codename = request.data.get('codename')
    description = request.data.get('description', '')
    category = request.data.get('category', 'custom')
    
    if not name or not codename:
        return Response({
            'error': 'Name and codename are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if permission already exists
    if Permission.objects.filter(codename=codename).exists():
        return Response({
            'error': 'Permission with this codename already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        permission = Permission.objects.create(
            name=name,
            codename=codename,
            description=description,
            category=category,
            is_active=True
        )
        
        return Response({
            'message': 'Permission created successfully',
            'permission': PermissionSerializer(permission).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to create permission: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_dynamic_permission(request):
    """
    Assign a permission to a user
    """
    if not request.user.is_superuser:
        return Response({
            'error': 'Only superusers can assign permissions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    permission_codename = request.data.get('permission_codename')
    
    if not user_id or not permission_codename:
        return Response({
            'error': 'User ID and permission codename are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
        
        # Create or update user permission
        user_permission, created = UserPermission.objects.get_or_create(
            user=user,
            permission=permission,
            defaults={'is_active': True}
        )
        
        if not created:
            user_permission.is_active = True
            user_permission.save()
        
        return Response({
            'message': 'Permission assigned successfully',
            'user_id': user.id,
            'permission_codename': permission.codename,
            'created': created
        })
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Permission.DoesNotExist:
        return Response({
            'error': 'Permission not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to assign permission: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_dynamic_permissions(request):
    """
    Get all permissions for the current user
    """
    user = request.user
    
    # Get direct permissions
    direct_permissions = UserPermission.objects.filter(
        user=user,
        is_active=True
    ).select_related('permission')
    
    # Get permissions through roles
    role_permissions = RolePermission.objects.filter(
        role__user_roles__user=user,
        is_active=True
    ).select_related('permission')
    
    # Combine and deduplicate
    all_permissions = set()
    
    for up in direct_permissions:
        all_permissions.add(up.permission.codename)
    
    for rp in role_permissions:
        all_permissions.add(rp.permission.codename)
    
    return Response({
        'user_id': user.id,
        'permissions': list(all_permissions),
        'permission_count': len(all_permissions)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_dynamic_permission(request):
    """
    Test if a permission works for the current user
    """
    permission_codename = request.data.get('permission_codename')
    
    if not permission_codename:
        return Response({
            'error': 'Permission codename is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Use the same logic as check_dynamic_permission
    return check_dynamic_permission(request)
