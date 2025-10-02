from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import transaction
from .permission_models import Permission
from .permission_serializers import PermissionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PermissionCreateView(generics.CreateAPIView):
    """Create new custom permission"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create a new custom permission",
        request_body=PermissionSerializer,
        responses={
            201: openapi.Response(description="Permission created successfully"),
            400: openapi.Response(description="Bad request - validation error"),
            403: openapi.Response(description="Admin permission required")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            permission = serializer.save()
            return Response({
                'success': True,
                'message': 'Permission created successfully',
                'data': PermissionSerializer(permission).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PermissionUpdateView(generics.UpdateAPIView):
    """Update existing permission"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['patch', 'put']

    @swagger_auto_schema(
        operation_description="Update an existing permission",
        request_body=PermissionSerializer,
        responses={
            200: openapi.Response(description="Permission updated successfully"),
            400: openapi.Response(description="Bad request - validation error"),
            404: openapi.Response(description="Permission not found"),
            403: openapi.Response(description="Admin permission required")
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            permission = self.get_object()
            serializer = self.get_serializer(permission, data=request.data, partial=True)
            if serializer.is_valid():
                updated_permission = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Permission updated successfully',
                    'data': PermissionSerializer(updated_permission).data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Permission not found'
            }, status=status.HTTP_404_NOT_FOUND)

class PermissionDeleteView(generics.DestroyAPIView):
    """Delete permission (soft delete)"""
    queryset = Permission.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Delete a permission (soft delete)",
        responses={
            200: openapi.Response(description="Permission deleted successfully"),
            404: openapi.Response(description="Permission not found"),
            403: openapi.Response(description="Admin permission required")
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            permission = self.get_object()
            # Soft delete - set is_active to False
            permission.is_active = False
            permission.save()
            return Response({
                'success': True,
                'message': 'Permission deleted successfully'
            }, status=status.HTTP_200_OK)
        except Permission.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Permission not found'
            }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Get permission details by ID",
    responses={
        200: openapi.Response(description="Permission details retrieved successfully"),
        404: openapi.Response(description="Permission not found"),
        403: openapi.Response(description="Admin permission required")
    }
)
def get_permission_details(request, permission_id):
    """Get detailed information about a specific permission"""
    try:
        permission = Permission.objects.get(id=permission_id, is_active=True)
        serializer = PermissionSerializer(permission)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Permission.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Permission not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@swagger_auto_schema(
    operation_description="Bulk create permissions",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'permissions': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'codename': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'category': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        required=['permissions']
    ),
    responses={
        201: openapi.Response(description="Permissions created successfully"),
        400: openapi.Response(description="Bad request - validation error"),
        403: openapi.Response(description="Admin permission required")
    }
)
def bulk_create_permissions(request):
    """Create multiple permissions at once"""
    permissions_data = request.data.get('permissions', [])
    
    if not permissions_data:
        return Response({
            'success': False,
            'message': 'No permissions data provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_permissions = []
    errors = []
    
    with transaction.atomic():
        for perm_data in permissions_data:
            serializer = PermissionSerializer(data=perm_data)
            if serializer.is_valid():
                permission = serializer.save()
                created_permissions.append(PermissionSerializer(permission).data)
            else:
                errors.append({
                    'permission': perm_data,
                    'errors': serializer.errors
                })
    
    return Response({
        'success': True,
        'message': f'{len(created_permissions)} permissions created successfully',
        'data': created_permissions,
        'errors': errors if errors else None
    }, status=status.HTTP_201_CREATED)
