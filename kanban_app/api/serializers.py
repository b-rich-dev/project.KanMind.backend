from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField()
    #password = serializers.CharField(write_only=True)
    #repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']