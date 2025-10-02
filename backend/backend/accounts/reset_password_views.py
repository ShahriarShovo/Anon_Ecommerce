from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from accounts.send_reset_password_link import send_password_reset_email, verify_reset_token, clear_reset_token
from accounts.models import User

class ForgotPasswordView(APIView):
    """
    Handle forgot password requests
    POST /api/accounts/forgot-password/
    """
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email address is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send password reset email
        success, message = send_password_reset_email(email)
        
        if success:
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    """
    Handle password reset with token
    GET /api/accounts/reset-password/{token}/ - Validate token
    POST /api/accounts/reset-password/{token}/ - Reset password
    """
    
    def get(self, request, token):
        """Validate reset token"""
        is_valid, user, message = verify_reset_token(token)
        
        if is_valid:
            return Response({
                'success': True,
                'message': 'Token is valid',
                'user_email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, token):
        """Reset password with token"""
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not password or not confirm_password:
            return Response({
                'success': False,
                'message': 'Password and confirm password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return Response({
                'success': False,
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 6:
            return Response({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token
        is_valid, user, message = verify_reset_token(token)
        
        if not is_valid:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update password
            user.set_password(password)
            user.save()
            
            # Clear reset token
            clear_reset_token(user)
            
            return Response({
                'success': True,
                'message': 'Password has been reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while resetting the password'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
