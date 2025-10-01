from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .permission_models import Permission, Role, UserRole, UserPermission
from .permission_serializers import (
    UserPermissionListSerializer, UserRoleSerializer, 
    PermissionSerializer, RoleSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Get detailed permissions for a specific user",
    responses={
        200: openapi.Response(description="User permissions retrieved successfully"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def get_user_permission_details(request, user_id):
    """Get detailed permission information for a specific user"""
    try:
        user = User.objects.select_related('profile').get(id=user_id)
        
        # Get permissions from roles
        role_permissions = []
        for user_role in user.user_roles.select_related('role').prefetch_related('role__role_permissions__permission'):
            for role_perm in user_role.role.role_permissions.all():
                role_permissions.append({
                    'id': role_perm.permission.id,
                    'name': role_perm.permission.name,
                    'codename': role_perm.permission.codename,
                    'category': role_perm.permission.category,
                    'source': 'role',
                    'role_name': user_role.role.name
                })
        
        # Get direct permissions
        direct_permissions = []
        for direct_perm in user.direct_permissions.select_related('permission').all():
            direct_permissions.append({
                'id': direct_perm.permission.id,
                'name': direct_perm.permission.name,
                'codename': direct_perm.permission.codename,
                'category': direct_perm.permission.category,
                'source': 'direct'
            })
        
        # Get user roles
        user_roles = []
        for user_role in user.user_roles.select_related('role').all():
            user_roles.append({
                'id': user_role.role.id,
                'name': user_role.role.name,
                'description': user_role.role.description,
                'is_system_role': user_role.role.is_system_role
            })
        
        return Response({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.profile.full_name if hasattr(user, 'profile') else '',
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'role_permissions': role_permissions,
                'direct_permissions': direct_permissions,
                'user_roles': user_roles,
                'total_permissions': len(role_permissions) + len(direct_permissions)
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Assign roles to a user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'role_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description='List of role IDs to assign'
            )
        },
        required=['role_ids']
    ),
    responses={
        200: openapi.Response(description="Roles assigned successfully"),
        400: openapi.Response(description="Bad request - validation error"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def assign_user_roles(request, user_id):
    """Assign roles to a specific user"""
    try:
        user = User.objects.get(id=user_id)
        role_ids = request.data.get('role_ids', [])
        
        if not role_ids:
            return Response({
                'success': False,
                'message': 'No role IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate roles exist
        valid_roles = Role.objects.filter(id__in=role_ids, is_active=True)
        if len(valid_roles) != len(role_ids):
            return Response({
                'success': False,
                'message': 'Some roles not found or inactive'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Remove existing roles
            UserRole.objects.filter(user=user).delete()
            
            # Add new roles
            for role in valid_roles:
                UserRole.objects.create(
                    user=user,
                    role=role,
                    assigned_by=request.user
                )
        
        return Response({
            'success': True,
            'message': f'Successfully assigned {len(valid_roles)} roles to user'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Assign direct permissions to a user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'permission_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description='List of permission IDs to assign'
            )
        },
        required=['permission_ids']
    ),
    responses={
        200: openapi.Response(description="Permissions assigned successfully"),
        400: openapi.Response(description="Bad request - validation error"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def assign_user_direct_permissions(request, user_id):
    """Assign direct permissions to a specific user"""
    try:
        user = User.objects.get(id=user_id)
        permission_ids = request.data.get('permission_ids', [])
        
        if not permission_ids:
            return Response({
                'success': False,
                'message': 'No permission IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate permissions exist
        valid_permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
        if len(valid_permissions) != len(permission_ids):
            return Response({
                'success': False,
                'message': 'Some permissions not found or inactive'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Remove existing direct permissions
            UserPermission.objects.filter(user=user).delete()
            
            # Add new direct permissions
            for permission in valid_permissions:
                UserPermission.objects.create(
                    user=user,
                    permission=permission,
                    granted_by=request.user
                )
        
        return Response({
            'success': True,
            'message': f'Successfully assigned {len(valid_permissions)} direct permissions to user'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Remove all permissions from a user",
    responses={
        200: openapi.Response(description="User permissions removed successfully"),
        404: openapi.Response(description="User not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def remove_user_permissions(request, user_id):
    """Remove all permissions from a specific user"""
    try:
        user = User.objects.get(id=user_id)
        
        with transaction.atomic():
            # Remove all roles
            UserRole.objects.filter(user=user).delete()
            
            # Remove all direct permissions
            UserPermission.objects.filter(user=user).delete()
        
        return Response({
            'success': True,
            'message': 'All permissions removed from user'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Get users by role",
    responses={
        200: openapi.Response(description="Users retrieved successfully"),
        404: openapi.Response(description="Role not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def get_users_by_role(request, role_id):
    """Get all users assigned to a specific role"""
    try:
        role = Role.objects.get(id=role_id, is_active=True)
        
        users = User.objects.filter(
            user_roles__role=role,
            is_active=True
        ).select_related('profile').distinct()
        
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'email': user.email,
                'full_name': user.profile.full_name if hasattr(user, 'profile') else '',
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'last_login': user.last_login
            })
        
        return Response({
            'success': True,
            'data': {
                'role': {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                },
                'users': user_data,
                'user_count': len(user_data)
            }
        }, status=status.HTTP_200_OK)
        
    except Role.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Role not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Bulk assign permissions to multiple users",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description='List of user IDs'
            ),
            'permission_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description='List of permission IDs'
            ),
            'assignment_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['direct', 'role'],
                description='Type of assignment'
            )
        },
        required=['user_ids', 'permission_ids', 'assignment_type']
    ),
    responses={
        200: openapi.Response(description="Permissions assigned successfully"),
        400: openapi.Response(description="Bad request - validation error"),
        403: openapi.Response(description="Admin permission required")
    }
)
def bulk_assign_permissions(request):
    """Bulk assign permissions to multiple users"""
    user_ids = request.data.get('user_ids', [])
    permission_ids = request.data.get('permission_ids', [])
    assignment_type = request.data.get('assignment_type', 'direct')
    
    if not user_ids or not permission_ids:
        return Response({
            'success': False,
            'message': 'User IDs and permission IDs are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if assignment_type not in ['direct', 'role']:
        return Response({
            'success': False,
            'message': 'Assignment type must be "direct" or "role"'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate users exist
    valid_users = User.objects.filter(id__in=user_ids, is_active=True)
    if len(valid_users) != len(user_ids):
        return Response({
            'success': False,
            'message': 'Some users not found or inactive'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate permissions exist
    valid_permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
    if len(valid_permissions) != len(permission_ids):
        return Response({
            'success': False,
            'message': 'Some permissions not found or inactive'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    success_count = 0
    errors = []
    
    with transaction.atomic():
        for user in valid_users:
            try:
                if assignment_type == 'direct':
                    # Remove existing direct permissions
                    UserPermission.objects.filter(user=user).delete()
                    
                    # Add new direct permissions
                    for permission in valid_permissions:
                        UserPermission.objects.create(
                            user=user,
                            permission=permission,
                            granted_by=request.user
                        )
                else:  # role assignment
                    # This would require creating a new role or using existing role
                    # For now, we'll skip role assignment in bulk
                    pass
                
                success_count += 1
            except Exception as e:
                errors.append({
                    'user_id': user.id,
                    'error': str(e)
                })
    
    return Response({
        'success': True,
        'message': f'Successfully assigned permissions to {success_count} users',
        'success_count': success_count,
        'errors': errors if errors else None
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Assign permissions and roles to a specific user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'permission_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description="List of permission IDs to assign"
            ),
            'role_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description="List of role IDs to assign"
            )
        },
        required=['permission_ids', 'role_ids']
    ),
    responses={
        200: openapi.Response(description="Permissions and roles assigned successfully"),
        404: openapi.Response(description="User not found"),
        400: openapi.Response(description="Invalid data provided"),
        403: openapi.Response(description="Admin permission required")
    }
)
def assign_user_permissions(request, user_id):
    """Assign permissions and roles to a specific user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    permission_ids = request.data.get('permission_ids', [])
    role_ids = request.data.get('role_ids', [])
    
    if not permission_ids and not role_ids:
        return Response({
            'success': False,
            'error': 'At least one permission or role must be provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Assign direct permissions
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
                for permission in permissions:
                    UserPermission.objects.get_or_create(
                        user=user,
                        permission=permission,
                        defaults={'is_active': True}
                    )
            
            # Assign roles
            if role_ids:
                roles = Role.objects.filter(id__in=role_ids, is_active=True)
                for role in roles:
                    UserRole.objects.get_or_create(
                        user=user,
                        role=role,
                        defaults={'is_active': True}
                    )
            
            return Response({
                'success': True,
                'message': f'Successfully assigned {len(permission_ids)} permissions and {len(role_ids)} roles to user {user.email}',
                'user_id': user.id,
                'permission_count': len(permission_ids),
                'role_count': len(role_ids)
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to assign permissions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
