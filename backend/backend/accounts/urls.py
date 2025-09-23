
from django.urls import path
from accounts import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    path('signup/', views.Signup_user.as_view()),
    path('login/', views.User_login.as_view()),
    path('profile/', views.current_user),
    path('update-profile/<int:user_id>/', views.update_profile),
    path('change-password/', views.User_Change_Password.as_view()),
    path('users/', views.UserListView.as_view()),  # Admin users list
    path('users/<int:pk>/', views.UserDetailView.as_view()),  # User detail/update
    path('statistics/', views.admin_statistics),  # Admin dashboard statistics
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
