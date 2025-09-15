from rest_framework import permissions

class IsAdminOrStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin and staff users to create/edit/delete categories and subcategories.
    Read permissions are allowed to any request.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin and staff users
        return request.user and (request.user.is_staff or request.user.is_superuser)

class CanCreateCategory(permissions.BasePermission):
    """
    Permission to create categories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True

class CanEditCategory(permissions.BasePermission):
    """
    Permission to edit categories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True

class CanDeleteCategory(permissions.BasePermission):
    """
    Permission to delete categories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True

class CanCreateSubCategory(permissions.BasePermission):
    """
    Permission to create subcategories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True

class CanEditSubCategory(permissions.BasePermission):
    """
    Permission to edit subcategories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True

class CanDeleteSubCategory(permissions.BasePermission):
    """
    Permission to delete subcategories - only admin and staff
    """
    
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user and (request.user.is_staff or request.user.is_superuser)
        return True
