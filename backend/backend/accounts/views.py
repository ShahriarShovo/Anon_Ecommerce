from multiprocessing import context
from django.contrib.auth import login, logout, authenticate
from yaml import serialize
from accounts.models import Profile, User
from accounts.serializers import (UserRegistrationSerializers, 
LoginSerializer,ProfileSerializer,User_Password_Change_Serializer, UserListSerializer)
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta

# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class Signup_user(APIView):
    @swagger_auto_schema(
        operation_description="User registration endpoint",
        request_body=UserRegistrationSerializers,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "message": "Signup Successful",
                        "token": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        }
                    }
                }
            ),
            400: openapi.Response(description="Bad request - validation error")
        },
        tags=['Authentication']
    )
    def post(self, request, format=None):
        serializer = UserRegistrationSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            
            # Generate email verification token
            from accounts.email_verification_service import EmailVerificationService
            verification_token = EmailVerificationService.generate_verification_token()
            
            user.email_verification_token = verification_token
            user.email_verification_sent_at = timezone.now()
            user.is_email_verified = False  # Set to False initially
            user.save()
            
            # Send verification email
            email_sent = EmailVerificationService.send_verification_email(request, user, verification_token)
            
            if email_sent:
                return Response({
                    'message': 'Signup Successful! Please check your email to verify your account.',
                    'email_verification_sent': True,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Signup Successful! However, verification email could not be sent. Please contact support.',
                    'email_verification_sent': False,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
                
        return Response({'message':'Signup Failed'}, status=status.HTTP_400_BAD_REQUEST)



class User_login(APIView):
    @swagger_auto_schema(
        operation_description="User login endpoint",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login Successfull",
                        "token": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        }
                    }
                }
            ),
            404: openapi.Response(description="User not found or invalid credentials")
        },
        tags=['Authentication']
    )
    def post(self,request):
        form = LoginSerializer(data=request.data)
        if form.is_valid():
            email=form.data.get('email')
            password=form.data.get('password')
            user=authenticate(email=email, password=password)
            if user is not None:
                # Check if email is verified
                if not user.is_email_verified:
                    return Response({
                        'message': 'Please verify your email address before logging in. Check your email for verification link.',
                        'email_verification_required': True,
                        'email': user.email
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update last login timestamp
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                token=get_tokens_for_user(user)
                
                # Determine user type
                user_type = 'admin' if (user.is_staff or user.is_superuser) else 'customer'
                
                return Response({
                    'message':'Login Successfull', 
                    'token':token,
                    'user_type': user_type,
                    'is_admin': user.is_staff or user.is_superuser,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                    'email_verified': user.is_email_verified
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message':'User no Found'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'message':'User no Found'}, status=status.HTTP_404_NOT_FOUND)



@swagger_auto_schema(
    method='get',
    operation_description="Get current user profile",
    responses={
        200: openapi.Response(
            description="User profile retrieved successfully",
            schema=ProfileSerializer
        ),
        401: openapi.Response(description="Authentication required")
    },
    tags=['Profile'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    Profile_serializer = ProfileSerializer(profile) 
    return Response(Profile_serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_last_login(request):
    """
    Get current user's last login information
    """
    user = request.user
    
    return Response({
        'user_id': user.id,
        'email': user.email,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Update user profile",
    request_body=ProfileSerializer,
    responses={
        200: openapi.Response(
            description="Profile updated successfully",
            schema=ProfileSerializer
        ),
        400: openapi.Response(description="Bad request - validation error"),
        401: openapi.Response(description="Authentication required")
    },
    tags=['Profile'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request, user_id):
    try:
        # print('request  data = ', request.data)
        profile = Profile.objects.get(user__id=user_id)
        update_serializer=ProfileSerializer(profile, data=request.data)
        
        if update_serializer.is_valid():
            update_serializer.save(user=request.user)
            return Response(update_serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'message':'error'})

    except Exception as e:
        print(e)
        return Response({'message':'Data is not Valided'})



class User_Change_Password(APIView):
    permission_classes=[IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=User_Password_Change_Serializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password Changed Successfully"
                    }
                }
            ),
            400: openapi.Response(description="Bad request - validation error"),
            401: openapi.Response(description="Authentication required")
        },
        tags=['Authentication'],
        security=[{'Bearer': []}]
    )
    def post(self, request, format=None):
        serialize = User_Password_Change_Serializer(data=request.data, context={'user':request.user})
        if serialize.is_valid():
            return Response({'message':'Password Changed Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'Failed to Change Password'}, status=status.HTTP_400_BAD_REQUEST)
            



# class UserPasswordChangedView(APIView):
#     def post(self, request, format=None):
#         permission_classes=[IsAuthenticated]
#         serializer = UserPasswordChangedSerializer(data=request.data, context={'user':request.user})
#         if serializer.is_valid(raise_exception=True):
#             return Response({'message':'Password Changed Successfully'}, status=status.HTTP_200_OK)
#         return Response({'message':'Failed to Change Password'}, status=status.HTTP_400_BAD_REQUEST)


# Admin Users Management APIs
class UserListView(generics.ListAPIView):
    """
    List all users (admin only)
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        # Admin can see all users
        return User.objects.select_related('profile').all().order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user details (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        # Admin can access any user
        return User.objects.select_related('profile').all()


# Admin Statistics API
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_statistics(request):
    """
    Get admin dashboard statistics
    """
    try:
        # Import here to avoid circular imports
        from orders.models.orders.order import Order
        from products.models.products.product import Product
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta
        
        # Total Orders Count
        total_orders = Order.objects.count()
        
        # Total Products Count (excluding archived)
        total_products = Product.objects.filter(status='active').count()
        
        # Total Users Count
        total_users = User.objects.count()
        
        # Total Revenue (sum of all delivered orders)
        total_revenue = Order.objects.filter(
            status='delivered'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Recent Orders (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_orders = Order.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # Active Users (users who logged in last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        active_users = User.objects.filter(
            last_login__gte=month_ago
        ).count()
        
        statistics = {
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users,
            'total_revenue': float(total_revenue),
            'recent_orders': recent_orders,
            'active_users': active_users,
        }
        
        return Response({
            'success': True,
            'data': statistics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailVerificationView(APIView):
    """
    Email verification endpoint
    """
    @swagger_auto_schema(
        operation_description="Verify user email with token",
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                examples={
                    "application/json": {
                        "message": "Email verified successfully!",
                        "verified": True
                    }
                }
            ),
            400: openapi.Response(description="Invalid or expired token"),
            404: openapi.Response(description="User not found")
        },
        tags=['Authentication']
    )
    def get(self, request, token):
        """
        Verify email with token
        """
        try:
            print(f"🔍 DEBUG: Email verification request for token: {token}")
            
            # Find user by verification token (check both verified and unverified)
            user = User.objects.filter(email_verification_token=token).first()
            print(f"🔍 DEBUG: User found: {user}")
            
            if user:
                print(f"🔍 DEBUG: User email: {user.email}")
                print(f"🔍 DEBUG: User verification status: {user.is_email_verified}")
                print(f"🔍 DEBUG: Token sent at: {user.email_verification_sent_at}")
                
                # Check if user is already verified
                if user.is_email_verified:
                    print(f"🔍 DEBUG: User is already verified")
                    return Response({
                        'message': 'Email is already verified! You can now log in to your account.',
                        'verified': True,
                        'email': user.email,
                        'already_verified': True
                    }, status=status.HTTP_200_OK)
            
            if not user:
                print(f"🔍 DEBUG: No user found with token: {token}")
                return Response({
                    'message': 'Invalid or expired verification token',
                    'verified': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if token is expired (24 hours)
            if user.email_verification_sent_at:
                token_age = timezone.now() - user.email_verification_sent_at
                if token_age > timedelta(hours=24):
                    return Response({
                        'message': 'Verification token has expired. Please request a new verification email.',
                        'verified': False
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify the email (handle race condition)
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
                print(f"🔍 DEBUG: User {user.email} email verified successfully")
                
                # Clear token after successful verification (with delay to handle race conditions)
                import threading
                def clear_token_after_delay():
                    import time
                    time.sleep(5)  # Wait 5 seconds
                    try:
                        user.refresh_from_db()
                        if user.is_email_verified:
                            user.email_verification_token = None
                            user.save()
                            print(f"🔍 DEBUG: Token cleared for user {user.email}")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error clearing token: {e}")
                
                # Run token cleanup in background
                threading.Thread(target=clear_token_after_delay, daemon=True).start()
                
                return Response({
                    'message': 'Email verified successfully! You can now log in to your account.',
                    'verified': True,
                    'email': user.email,
                    'redirect_url': '/email-verified'
                }, status=status.HTTP_200_OK)
            else:
                print(f"🔍 DEBUG: User {user.email} already verified")
                return Response({
                    'message': 'Email is already verified! You can now log in to your account.',
                    'verified': True,
                    'email': user.email,
                    'already_verified': True
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Error verifying email: {str(e)}',
                'verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationEmailView(APIView):
    """
    Resend verification email endpoint
    """
    @swagger_auto_schema(
        operation_description="Resend verification email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="Verification email sent successfully",
                examples={
                    "application/json": {
                        "message": "Verification email sent successfully!",
                        "email_sent": True
                    }
                }
            ),
            400: openapi.Response(description="User not found or already verified"),
            500: openapi.Response(description="Failed to send email")
        },
        tags=['Authentication']
    )
    def post(self, request):
        """
        Resend verification email
        """
        try:
            email = request.data.get('email')
            print(f"🔍 DEBUG: Resend verification request data: {request.data}")
            print(f"🔍 DEBUG: Email from request: {email}")
            print(f"🔍 DEBUG: Email type: {type(email)}")
            print(f"🔍 DEBUG: Email length: {len(email) if email else 'None'}")
            print(f"🔍 DEBUG: Email repr: {repr(email)}")
            
            if not email:
                return Response({
                    'message': 'Email is required',
                    'email_sent': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find user by email (case insensitive)
            user = User.objects.filter(email__iexact=email).first()
            print(f"🔍 DEBUG: User found: {user}")
            print(f"🔍 DEBUG: User email: {user.email if user else 'None'}")
            print(f"🔍 DEBUG: User verification status: {user.is_email_verified if user else 'None'}")
            print(f"🔍 DEBUG: All users with similar email: {list(User.objects.filter(email__icontains=email.split('@')[0]).values_list('email', flat=True))}")
            
            if not user:
                return Response({
                    'message': 'User not found',
                    'email_sent': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already verified
            if user.is_email_verified:
                return Response({
                    'message': 'Email is already verified',
                    'email_sent': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate new verification token
            from accounts.email_verification_service import EmailVerificationService
            verification_token = EmailVerificationService.generate_verification_token()
            user.email_verification_token = verification_token
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email
            email_sent = EmailVerificationService.send_verification_email(request, user, verification_token)
            
            if email_sent:
                return Response({
                    'message': 'Verification email sent successfully!',
                    'email_sent': True,
                    'email': user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Failed to send verification email. Please try again later.',
                    'email_sent': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'message': f'Error sending verification email: {str(e)}',
                'email_sent': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







