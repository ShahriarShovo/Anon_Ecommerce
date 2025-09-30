
from django.urls import path
from accounts import views
from accounts.reset_password_views import ForgotPasswordView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    path('signup/', views.Signup_user.as_view()),
    path('register/', views.Signup_user.as_view()),  # Alias for frontend compatibility
    path('login/', views.User_login.as_view()),
    path('profile/', views.current_user),
    path('update-profile/<int:user_id>/', views.update_profile),
    path('change-password/', views.User_Change_Password.as_view()),
    path('users/', views.UserListView.as_view()),  # Admin users list
    path('users/<int:pk>/', views.UserDetailView.as_view()),  # User detail/update
    path('statistics/', views.admin_statistics),  # Admin dashboard statistics
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email verification URLs
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
    
    # Password reset URLs
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]
