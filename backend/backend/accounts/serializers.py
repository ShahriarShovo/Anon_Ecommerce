from xml.dom import ValidationErr
from django.forms import ValidationError
from rest_framework import serializers
from accounts.models import User
from accounts.models import Profile
from rest_framework import status
from rest_framework.response import Response



class UserRegistrationSerializers(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    full_name = serializers.CharField(max_length=264, required=True)
    
    class Meta:
        model = User
        fields = ['email','password', 'confirm_password', 'full_name']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password=attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('Password and Confirm Password Doesnt match')
        else:
            return attrs

    def create(self, validated_data):
        # Remove confirm_password and full_name from validated_data
        confirm_password = validated_data.pop('confirm_password', None)
        full_name = validated_data.pop('full_name', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Generate unique username from email and full_name
        email_username = user.email.split('@')[0]  # Get part before @
        base_username = f"{email_username}_{full_name.replace(' ', '_').lower()}"
        
        # Make username unique by adding numbers if needed
        username = base_username
        counter = 1
        while Profile.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Update profile with generated username and full_name
        profile = user.profile
        profile.username = username
        profile.full_name = full_name
        profile.save()
        
        return user



class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model=User
        fields=['email','password']



class ProfileSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    email_verified = serializers.BooleanField(source='user.is_email_verified', read_only=True)
    
    class Meta:
        model = Profile
        fields=['id', 'email', 'username', 'full_name', 'address', 'city', 'zipcode', 'country', 'phone', 'is_staff', 'is_superuser', 'email_verified']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin only)
    """
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)
    username = serializers.CharField(source='profile.username', read_only=True)
    addresses = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'username', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'addresses', 'orders_count', 'total_spent']
    
    def get_addresses(self, obj):
        """Get all addresses for the user"""
        from orders.models.orders.address import Address
        addresses = Address.objects.filter(user=obj)
        return [
            {
                'id': addr.id,
                'address_type': addr.address_type,
                'full_name': addr.full_name,
                'phone_number': addr.phone_number,
                'address_line_1': addr.address_line_1,
                'address_line_2': addr.address_line_2,
                'city': addr.city,
                'postal_code': addr.postal_code,
                'country': addr.country,
                'is_default': addr.is_default
            }
            for addr in addresses
        ]
    
    def get_orders_count(self, obj):
        """Get total number of orders for the user"""
        from orders.models.orders.order import Order
        return Order.objects.filter(user=obj).count()
    
    def get_total_spent(self, obj):
        """Get total amount spent by the user"""
        from orders.models.orders.order import Order
        from django.db.models import Sum
        total = Order.objects.filter(user=obj).aggregate(
            total=Sum('total_amount')
        )['total']
        return float(total) if total else 0.0


class User_Password_Change_Serializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
       
        fields=['password','confirm_password']

    def validate(self, attrs):
        password= attrs.get('password')
        confirm_password=attrs.get('confirm_password')
        user = self.context.get('user')
        if password != confirm_password :
            raise ValueError('Password Doesnt match')
        else:
            user.set_password(password)
            user.save()
            return attrs      



# class UserPasswordChangedSerializer(serializers.Serializer):
#     password = serializers.CharField(style={'input_type':'password'}, write_only=True)
#     confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)

#     class Meta:
#         fields = ['password','confirm_password']

#     def validate(self, attrs):
#         password = attrs.get('password')
#         confirm_password = attrs.get('confirm_password')
#         user=self.context.get('user')
#         if password != confirm_password:
#             raise ValidationError("Password Doesn't match")
#         user.set_password(password)
#         user.save()
#         return attrs


        