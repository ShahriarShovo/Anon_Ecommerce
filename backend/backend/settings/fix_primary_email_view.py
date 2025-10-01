from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .email_model import EmailSettings
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fix_primary_emails(request):
    """
    Fix multiple primary email settings by keeping only one primary
    """
    try:
        with transaction.atomic():
            # Get all primary email settings
            primary_emails = EmailSettings.objects.filter(is_primary=True)
            
            if primary_emails.count() <= 1:
                return Response({
                    'success': True,
                    'message': 'No fix needed - only one or no primary emails found',
                    'primary_count': primary_emails.count()
                }, status=status.HTTP_200_OK)
            
            # Keep the first one as primary, unset others
            first_primary = primary_emails.first()
            others = primary_emails.exclude(id=first_primary.id)
            
            # Unset primary for others
            others.update(is_primary=False)
            
            # Verify the fix
            remaining_primary = EmailSettings.objects.filter(is_primary=True)
            
            return Response({
                'success': True,
                'message': f'Fixed! Kept ID {first_primary.id} as primary, unset {others.count()} others',
                'primary_count': remaining_primary.count(),
                'kept_primary': {
                    'id': first_primary.id,
                    'name': first_primary.name,
                    'email': first_primary.email_address
                }
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Fix Primary Emails Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to fix primary emails: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_primary_emails(request):
    """
    Check current primary email settings status
    """
    try:
        primary_emails = EmailSettings.objects.filter(is_primary=True)
        
        primary_list = []
        for email in primary_emails:
            primary_list.append({
                'id': email.id,
                'name': email.name,
                'email': email.email_address,
                'created_by': email.created_by.username,
                'is_active': email.is_active
            })
        
        return Response({
            'success': True,
            'primary_count': primary_emails.count(),
            'primary_emails': primary_list,
            'needs_fix': primary_emails.count() > 1
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Check Primary Emails Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to check primary emails: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_primary_email(request):
    """
    Switch primary email to a different email setting
    """
    try:
        email_id = request.data.get('email_id')
        if not email_id:
            return Response({
                'success': False,
                'message': 'Email ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Get the email setting to make primary
            try:
                email_setting = EmailSettings.objects.get(id=email_id)
            except EmailSettings.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Email setting not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Unset all other primary emails
            EmailSettings.objects.exclude(id=email_id).update(is_primary=False)
            
            # Set this email as primary
            email_setting.is_primary = True
            email_setting.is_active = True
            email_setting.save()
            
            return Response({
                'success': True,
                'message': f'Successfully switched primary email to {email_setting.name}',
                'new_primary': {
                    'id': email_setting.id,
                    'name': email_setting.name,
                    'email': email_setting.email_address
                }
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Switch Primary Email Error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to switch primary email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
