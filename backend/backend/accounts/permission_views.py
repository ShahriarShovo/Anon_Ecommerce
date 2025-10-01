from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .permission_models import Permission, Role, RolePermission, UserRole, UserPermission
from .permission_serializers import (
    PermissionSerializer, RoleSerializer, RoleDetailSerializer, 
    UserRoleSerializer, UserPermissionSerializer, UserPermissionAssignmentSerializer,
    UserPermissionListSerializer, PermissionCheckSerializer
)

User = get_user_model()


class PermissionListView(generics.ListAPIView):
    """List all permissions"""
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })


class RoleListView(generics.ListCreateAPIView):
    """List and create roles"""
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })

    def perform_create(self, serializer):
        serializer.save()


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a role"""
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_destroy(self, instance):
        if instance.is_system_role:
            raise serializers.ValidationError("Cannot delete system roles")
        instance.is_active = False
        instance.save()


class RolePermissionView(generics.ListCreateAPIView):
    """Manage permissions for a specific role"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        role_id = self.kwargs['role_id']
        return Permission.objects.filter(
            permission_roles__role_id=role_id,
            is_active=True
        )

    def create(self, request, *args, **kwargs):
        role_id = self.kwargs['role_id']
        permission_ids = request.data.get('permission_ids', [])
        
        try:
            role = Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Remove existing permissions
            RolePermission.objects.filter(role=role).delete()
            
            # Add new permissions
            for permission_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=permission_id, is_active=True)
                    RolePermission.objects.create(role=role, permission=permission)
                except Permission.DoesNotExist:
                    continue

        return Response({'message': 'Role permissions updated successfully'})


class UserPermissionListView(generics.ListAPIView):
    """List all users with their permissions"""
    queryset = User.objects.filter(is_staff=True).prefetch_related(
        'user_roles__role', 'direct_permissions__permission'
    )
    serializer_class = UserPermissionListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserPermissionAssignmentView(generics.CreateAPIView):
    """Assign permissions and roles to a user"""
    serializer_class = UserPermissionAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        permission_ids = serializer.validated_data.get('permission_ids', [])
        role_ids = serializer.validated_data.get('role_ids', [])

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Clear existing roles and permissions
            UserRole.objects.filter(user=user).delete()
            UserPermission.objects.filter(user=user).delete()

            # Assign new roles
            for role_id in role_ids:
                try:
                    role = Role.objects.get(id=role_id, is_active=True)
                    UserRole.objects.create(user=user, role=role, assigned_by=request.user)
                except Role.DoesNotExist:
                    continue

            # Assign direct permissions
            for permission_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=permission_id, is_active=True)
                    UserPermission.objects.create(user=user, permission=permission, granted_by=request.user)
                except Permission.DoesNotExist:
                    continue

        return Response({'message': 'User permissions updated successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_permissions(request):
    """Get current user's permissions"""
    user = request.user
    
    # Get permissions from roles
    role_permissions = set()
    for user_role in user.user_roles.select_related('role').prefetch_related('role__role_permissions__permission'):
        for role_perm in user_role.role.role_permissions.all():
            role_permissions.add(role_perm.permission.codename)

    # Get direct permissions
    direct_permissions = set(user.direct_permissions.values_list('permission__codename', flat=True))

    # Combine both
    all_permissions = role_permissions.union(direct_permissions)
    
    return Response({
        'permissions': list(all_permissions),
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """Check if user has specific permission"""
    serializer = PermissionCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    permission_codename = serializer.validated_data['permission_codename']
    user_id = serializer.validated_data.get('user_id')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user

    # Superuser has all permissions
    if user.is_superuser:
        return Response({'has_permission': True})

    # Check role permissions
    has_role_permission = UserRole.objects.filter(
        user=user,
        role__role_permissions__permission__codename=permission_codename,
        role__is_active=True
    ).exists()

    # Check direct permissions
    has_direct_permission = UserPermission.objects.filter(
        user=user,
        permission__codename=permission_codename
    ).exists()

    has_permission = has_role_permission or has_direct_permission

    return Response({'has_permission': has_permission})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_permission_categories(request):
    """Get all permission categories"""
    categories = Permission.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    return Response({'categories': list(categories)})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_default_permissions(request):
    """Create default system permissions"""
    default_permissions = [
        {'name': 'Dashboard Access', 'codename': 'view_dashboard', 'category': 'dashboard'},
        {'name': 'Manage Products', 'codename': 'manage_products', 'category': 'products'},
        {'name': 'Manage Orders', 'codename': 'manage_orders', 'category': 'orders'},
        {'name': 'Manage Archived Products', 'codename': 'manage_archived_products', 'category': 'products'},
        {'name': 'Manage Categories', 'codename': 'manage_categories', 'category': 'products'},
        {'name': 'Manage Subcategories', 'codename': 'manage_subcategories', 'category': 'products'},
        {'name': 'Manage Users', 'codename': 'view_user', 'category': 'users'},
        {'name': 'Manage Admin Staff', 'codename': 'manage_admin_staff', 'category': 'users'},
        {'name': 'Manage Permissions', 'codename': 'manage_permissions', 'category': 'users'},
        {'name': 'Inbox Access', 'codename': 'inbox_access', 'category': 'communication'},
        {'name': 'Contact Messages', 'codename': 'view_contacts', 'category': 'communication'},
        {'name': 'Order Tracking', 'codename': 'order_tracking', 'category': 'orders'},
        {'name': 'Reports Access', 'codename': 'view_reports', 'category': 'reports'},
        {'name': 'Settings Access', 'codename': 'manage_settings', 'category': 'settings'},
    ]

    created_permissions = []
    for perm_data in default_permissions:
        try:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data
            )
            if created:
                created_permissions.append(permission.name)
        except Exception as e:
            # Skip if permission already exists or other error
            print(f"Permission {perm_data['codename']} already exists or error: {e}")
            continue

    # Create default roles
    default_roles = [
        {
            'name': 'Super Admin',
            'description': 'Full system access with all permissions',
            'is_system_role': True,
            'permissions': [perm['codename'] for perm in default_permissions]
        },
        {
            'name': 'Product Manager',
            'description': 'Can manage products, categories, and orders',
            'is_system_role': True,
            'permissions': [
                'view_dashboard', 'manage_products', 'manage_orders', 
                'manage_categories', 'manage_subcategories', 'order_tracking'
            ]
        },
        {
            'name': 'Customer Support',
            'description': 'Can handle customer inquiries and order tracking',
            'is_system_role': True,
            'permissions': [
                'view_dashboard', 'manage_orders', 'inbox_access', 
                'view_contacts', 'order_tracking'
            ]
        },
        {
            'name': 'Content Manager',
            'description': 'Can manage products and categories',
            'is_system_role': True,
            'permissions': [
                'view_dashboard', 'manage_products', 'manage_categories', 
                'manage_subcategories', 'manage_archived_products'
            ]
        }
    ]

    created_roles = []
    for role_data in default_roles:
        try:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'is_system_role': role_data['is_system_role']
                }
            )
            if created:
                created_roles.append(role.name)
                # Assign permissions to role
                for perm_codename in role_data['permissions']:
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        RolePermission.objects.get_or_create(role=role, permission=permission)
                    except Permission.DoesNotExist:
                        pass  # Skip if permission doesn't exist
        except Exception as e:
            # Skip if role already exists or other error
            print(f"Role {role_data['name']} already exists or error: {e}")
            continue

    return Response({
        'message': f'Successfully processed permissions and roles. Created {len(created_permissions)} new permissions and {len(created_roles)} new roles.',
        'permissions': created_permissions,
        'roles': created_roles,
        'success': True
    })
