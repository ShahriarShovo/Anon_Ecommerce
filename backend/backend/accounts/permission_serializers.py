from rest_framework import serializers
from django.contrib.auth import get_user_model
from .permission_models import Permission, Role, RolePermission, UserRole, UserPermission

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description', 'category', 'is_active', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'is_system_role', 'permission_count', 'user_count', 'created_at']

    def get_permission_count(self, obj):
        return obj.role_permissions.count()

    def get_user_count(self, obj):
        return obj.role_users.count()


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(source='role_permissions.permission', many=True, read_only=True)
    users = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'is_system_role', 'permissions', 'users', 'created_at']

    def get_users(self, obj):
        users = obj.role_users.all()
        return [{'id': user.user.id, 'email': user.user.email, 'full_name': getattr(user.user.profile, 'full_name', '')} for user in users]


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)

    class Meta:
        model = RolePermission
        fields = ['id', 'permission', 'permission_name', 'permission_codename', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_email = serializers.CharField(source='assigned_by.email', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'role', 'role_name', 'assigned_by', 'assigned_by_email', 'created_at']


class UserPermissionSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    granted_by_email = serializers.CharField(source='granted_by.email', read_only=True)

    class Meta:
        model = UserPermission
        fields = ['id', 'permission', 'permission_name', 'permission_codename', 'granted_by', 'granted_by_email', 'created_at']


class UserPermissionAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning permissions to users"""
    user_id = serializers.IntegerField()
    permission_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    role_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return value

    def validate_permission_ids(self, value):
        if value:
            existing_permissions = Permission.objects.filter(id__in=value, is_active=True)
            if len(existing_permissions) != len(value):
                raise serializers.ValidationError("Some permissions do not exist or are inactive")
        return value

    def validate_role_ids(self, value):
        if value:
            existing_roles = Role.objects.filter(id__in=value, is_active=True)
            if len(existing_roles) != len(value):
                raise serializers.ValidationError("Some roles do not exist or are inactive")
        return value


class UserPermissionListSerializer(serializers.ModelSerializer):
    """Serializer for listing user permissions"""
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_staff', 'is_superuser', 'roles', 'permissions']

    def get_roles(self, obj):
        user_roles = obj.user_roles.select_related('role').all()
        return [{'id': ur.role.id, 'name': ur.role.name} for ur in user_roles]

    def get_permissions(self, obj):
        # Get permissions from roles
        role_permissions = set()
        for user_role in obj.user_roles.select_related('role').prefetch_related('role__role_permissions__permission'):
            for role_perm in user_role.role.role_permissions.all():
                role_permissions.add(role_perm.permission.codename)

        # Get direct permissions
        direct_permissions = set(obj.direct_permissions.values_list('permission__codename', flat=True))

        # Combine both
        all_permissions = role_permissions.union(direct_permissions)
        return list(all_permissions)


class PermissionCheckSerializer(serializers.Serializer):
    """Serializer for checking user permissions"""
    permission_codename = serializers.CharField()
    user_id = serializers.IntegerField(required=False)

    def validate_permission_codename(self, value):
        try:
            Permission.objects.get(codename=value, is_active=True)
        except Permission.DoesNotExist:
            raise serializers.ValidationError("Permission does not exist or is inactive")
        return value
