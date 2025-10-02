from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from ...models.contact.contact import Contact
from ...serializers.contact.contact import ContactSerializer, ContactCreateSerializer, ContactUpdateSerializer

class ContactListCreateView(generics.ListCreateAPIView):
    """
    List and create contact messages
    """
    queryset = Contact.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]  # Allow anyone to create contact messages
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactSerializer
    
    def get_permissions(self):
        """
        Set permissions based on request method
        """
        if self.request.method == 'GET':
            # Only admin can view contact messages
            return [IsAdminUser()]
        else:
            # Anyone can create contact messages
            return [AllowAny()]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new contact message
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.',
                'data': {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'subject': contact.subject,
                    'created_at': contact.created_at
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send message. Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and delete contact messages (admin only)
    """
    queryset = Contact.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContactUpdateSerializer
        return ContactSerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])
def contact_stats(request):
    """
    Get contact message statistics for admin dashboard
    """
    try:
        total_contacts = Contact.objects.count()
        new_contacts = Contact.objects.filter(is_read=False).count()
        read_contacts = Contact.objects.filter(is_read=True, is_replied=False).count()
        replied_contacts = Contact.objects.filter(is_replied=True).count()
        
        return Response({
            'success': True,
            'data': {
                'total_contacts': total_contacts,
                'new_contacts': new_contacts,
                'read_contacts': read_contacts,
                'replied_contacts': replied_contacts
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def mark_as_read(request, contact_id):
    """
    Mark a contact message as read
    """
    try:
        contact = get_object_or_404(Contact, id=contact_id)
        contact.is_read = True
        contact.save()
        
        return Response({
            'success': True,
            'message': 'Contact message marked as read'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def mark_as_replied(request, contact_id):
    """
    Mark a contact message as replied
    """
    try:
        contact = get_object_or_404(Contact, id=contact_id)
        contact.is_read = True
        contact.is_replied = True
        contact.save()
        
        return Response({
            'success': True,
            'message': 'Contact message marked as replied'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
