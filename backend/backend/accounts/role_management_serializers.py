from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class AdminStaffUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    username = serializers.CharField(source='profile.username', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'username', 'phone', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']


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

