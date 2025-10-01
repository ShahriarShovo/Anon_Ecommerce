from django.urls import path
from . import advanced_user_permission_views

urlpatterns = [
    # Advanced User Permission Management
    path('users/<int:user_id>/permission-details/', advanced_user_permission_views.get_user_permission_details, name='user-permission-details'),
    path('users/<int:user_id>/assign-roles/', advanced_user_permission_views.assign_user_roles, name='user-assign-roles'),
    path('users/<int:user_id>/assign-direct-permissions/', advanced_user_permission_views.assign_user_direct_permissions, name='user-assign-direct-permissions'),
    path('users/<int:user_id>/assign-permissions/', advanced_user_permission_views.assign_user_permissions, name='user-assign-permissions'),
    path('users/<int:user_id>/remove-permissions/', advanced_user_permission_views.remove_user_permissions, name='user-remove-permissions'),
    path('roles/<int:role_id>/users/', advanced_user_permission_views.get_users_by_role, name='role-users'),
    path('permissions/bulk-assign/', advanced_user_permission_views.bulk_assign_permissions, name='bulk-assign-permissions'),
]
