from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.   
    Handles user registration with fullname instead of separate first_name and last_name fields.
    Validates that passwords match and email is unique before creating a new user account.
    Automatically creates an authentication token for the new user.
    """
    fullname = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'password', 'repeated_password']
    
    def to_representation(self, instance):
        """
        Combines first_name and last_name into fullname for the response.
        Args:
            instance: The User model instance          
        Returns:
            dict: Serialized data with fullname instead of separate name fields
        """
        data = super().to_representation(instance)
        data['fullname'] = f"{instance.first_name} {instance.last_name}".strip()
        return data

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        fullname = validated_data.pop('fullname')
        
        name_parts = fullname.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        Token.objects.create(user=user)

        return user