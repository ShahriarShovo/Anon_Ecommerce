from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminStaffUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    username = serializers.CharField(source='profile.username', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)
    last_login_formatted = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'username', 'phone', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'last_login_formatted']
    
    def get_last_login_formatted(self, obj):
        if obj.last_login:
            # Convert to Bangladesh timezone and format in 12-hour format
            from django.utils import timezone
            import pytz
            
            # Get Bangladesh timezone
            bd_tz = pytz.timezone('Asia/Dhaka')
            
            # Convert UTC datetime to Bangladesh timezone
            if obj.last_login.tzinfo is None:
                # If naive datetime, assume it's UTC
                utc_dt = pytz.utc.localize(obj.last_login)
            else:
                utc_dt = obj.last_login.astimezone(pytz.utc)
            
            bd_dt = utc_dt.astimezone(bd_tz)
            
            # Format in 12-hour format with AM/PM
            return bd_dt.strftime('%Y-%m-%d %I:%M:%S %p')
        return 'Never'

class SetUserRoleSerializer(serializers.Serializer):
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if 'is_staff' not in attrs and 'is_superuser' not in attrs:
            raise serializers.ValidationError('Provide at least one of is_staff or is_superuser')
        return attrs

class CreateAdminUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        if not attrs.get('is_staff') and not attrs.get('is_superuser'):
            raise serializers.ValidationError('User must have at least one role (staff or superuser).')
        return attrs

