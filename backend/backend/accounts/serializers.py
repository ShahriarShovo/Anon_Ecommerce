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
    
    class Meta:
        model = Profile
        fields=['username', 'full_name', 'address', 'city', 'zipcode', 'country', 'phone', 'is_staff', 'is_superuser']


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


        