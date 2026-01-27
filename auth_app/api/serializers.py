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
        """
        Validates that password and repeated_password match.
        
        Args:
            data: Dictionary containing all field data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If passwords do not match
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data
    
    def validate_email(self, value):
        """
        Validates that the email address is unique.
        
        Args:
            value: The email address to validate
            
        Returns:
            str: The validated email address
            
        Raises:
            ValidationError: If email already exists in the database
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        """
        Creates a new user with the validated data.
        
        Splits fullname into first_name and last_name, uses email as username,
        and automatically creates an authentication token for the new user.
        
        Args:
            validated_data: Dictionary containing validated registration data
            
        Returns:
            User: The newly created User instance
        """
        validated_data.pop('repeated_password')
        fullname = validated_data.pop('fullname')
        
        # Split fullname into first_name and last_name
        name_parts = fullname.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=validated_data['email'],  # Email is used as username for login
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        Token.objects.create(user=user)

        return user