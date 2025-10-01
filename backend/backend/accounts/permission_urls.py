from django.urls import path
from . import permission_views

urlpatterns = [
    # Permission management
    path('permissions/', permission_views.PermissionListView.as_view(), name='permission-list'),
    path('permissions/categories/', permission_views.get_permission_categories, name='permission-categories'),
    path('permissions/create-defaults/', permission_views.create_default_permissions, name='create-default-permissions'),
    
    # Role management
    path('roles/', permission_views.RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', permission_views.RoleDetailView.as_view(), name='role-detail'),
    path('roles/<int:role_id>/permissions/', permission_views.RolePermissionView.as_view(), name='role-permissions'),
    
    # User permission management
    path('users/permissions/', permission_views.UserPermissionListView.as_view(), name='user-permission-list'),
    path('users/assign-permissions/', permission_views.UserPermissionAssignmentView.as_view(), name='user-assign-permissions'),
    
    # Permission checking
    path('check-permission/', permission_views.check_permission, name='check-permission'),
    path('user-permissions/', permission_views.get_user_permissions, name='user-permissions'),
]
