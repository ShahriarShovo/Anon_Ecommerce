from django.urls import path
from . import dynamic_permission_views

urlpatterns = [
    path('check-permission/', dynamic_permission_views.check_dynamic_permission, name='check_dynamic_permission'),
    path('create-permission/', dynamic_permission_views.create_dynamic_permission, name='create_dynamic_permission'),
    path('assign-permission/', dynamic_permission_views.assign_dynamic_permission, name='assign_dynamic_permission'),
    path('user-permissions/', dynamic_permission_views.get_user_dynamic_permissions, name='get_user_dynamic_permissions'),
    path('test-permission/', dynamic_permission_views.test_dynamic_permission, name='test_dynamic_permission'),
]
