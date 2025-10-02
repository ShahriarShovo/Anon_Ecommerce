from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError
from orders.models.orders.address import Address
from orders.serializers.orders.address_serializer import AddressSerializer

class AddressListView(generics.ListCreateAPIView):
    """
    List all addresses for the authenticated user or create a new address
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

        queryset = Address.objects.filter(user=user)

        # Check address isolation
        all_addresses = Address.objects.all()

        for addr in all_addresses:
            print(f"    Address ID {addr.id}: User {addr.user.id} ({addr.user.email})")
        
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(user=user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an address
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

        queryset = Address.objects.filter(user=user)

        return queryset
    
    def update(self, request, *args, **kwargs):
        user = request.user
        address_id = kwargs.get('pk')

        # Check if address exists and belongs to user
        try:
            address = Address.objects.get(id=address_id, user=user)

        except Address.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Address not found or you do not have permission to update it.',
                'error': 'address_not_found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            result = super().update(request, *args, **kwargs)

            return result
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to update address: {str(e)}',
                'error': 'update_failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        address_id = kwargs.get('pk')

        # Check if address exists and belongs to user
        try:
            address = Address.objects.get(id=address_id, user=user)

        except Address.DoesNotExist:

            return Response({
                'success': False,
                'message': 'Address not found or you do not have permission to delete it.',
                'error': 'address_not_found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            result = super().destroy(request, *args, **kwargs)

            return result
        except ProtectedError as e:

            return Response({
                'success': False,
                'message': 'Cannot delete this address because it is being used in an existing order. Please contact support if you need to remove it.',
                'error': 'protected_foreign_key'
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_address(request, address_id):
    """
    Set an address as default for the user
    """
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        
        # Unset all other default addresses for this user
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        return Response({
            'success': True,
            'message': 'Default address updated successfully',
            'address': AddressSerializer(address).data
        })
        
    except Address.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Address not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_default_address(request):
    """
    Get the default address for the authenticated user
    """
    try:
        address = Address.objects.filter(user=request.user, is_default=True).first()
        
        if address:
            return Response({
                'success': True,
                'address': AddressSerializer(address).data
            })
        else:
            return Response({
                'success': True,
                'address': None,
                'message': 'No default address found'
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
