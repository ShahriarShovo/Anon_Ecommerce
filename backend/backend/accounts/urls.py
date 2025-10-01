
from django.urls import path, include
from accounts import views
from accounts.reset_password_views import ForgotPasswordView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView
from .role_management_views import list_admins_and_staff, set_user_role, create_admin_user, check_email_exists
from .admin_user_management_views import AdminUserProfileUpdateView, admin_change_user_password, admin_get_user_details

urlpatterns = [
    
    path('signup/', views.Signup_user.as_view()),
    path('register/', views.Signup_user.as_view()),  # Alias for frontend compatibility
    path('login/', views.User_login.as_view()),
    path('profile/', views.current_user),
    path('update-profile/<int:user_id>/', views.update_profile),
    path('change-password/', views.User_Change_Password.as_view()),
    path('users/', views.UserListView.as_view()),  # Admin users list
    path('users/<int:pk>/', views.UserDetailView.as_view()),  # User detail/update
    # Role management (admin-only)
    path('users/admins-staff/', list_admins_and_staff),
    path('users/<int:user_id>/set-role/', set_user_role),
    path('users/create-admin/', create_admin_user),
    path('check-email/', check_email_exists),
    path('statistics/', views.admin_statistics),  # Admin dashboard statistics
    
    # Permission management URLs
    path('permissions/', include('accounts.permission_urls')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Admin user management URLs
    path('admin/users/<int:pk>/profile/', AdminUserProfileUpdateView.as_view(), name='admin-update-user-profile'),
    path('admin/users/change-password/', admin_change_user_password, name='admin-change-user-password'),
    path('admin/users/<int:user_id>/details/', admin_get_user_details, name='admin-get-user-details'),
    
    # Email verification URLs
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
    
    # Password reset URLs
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]
