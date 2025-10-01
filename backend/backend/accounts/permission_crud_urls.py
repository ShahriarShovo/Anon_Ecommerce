from django.urls import path
from . import permission_crud_views

urlpatterns = [
    # Permission CRUD operations
    path('permissions/create/', permission_crud_views.PermissionCreateView.as_view(), name='permission-create'),
    path('permissions/<int:pk>/update/', permission_crud_views.PermissionUpdateView.as_view(), name='permission-update'),
    path('permissions/<int:pk>/delete/', permission_crud_views.PermissionDeleteView.as_view(), name='permission-delete'),
    path('permissions/<int:permission_id>/details/', permission_crud_views.get_permission_details, name='permission-details'),
    path('permissions/bulk-create/', permission_crud_views.bulk_create_permissions, name='permission-bulk-create'),
]
