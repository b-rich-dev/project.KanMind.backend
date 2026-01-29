from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer


class RegisterView(APIView):
    """
    API view for user registration.   
    Allows any user to register a new account by providing fullname, email, and password.
    Automatically creates an authentication token for the new user.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "token": user.auth_token.key,
                "fullname": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user authentication.   
    Authenticates users with email and password (email is used as username).
    Returns or creates an authentication token upon successful login.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=email, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "fullname": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    """
    API view for user logout.    
    Requires authentication. Deletes the user's authentication token to log them out.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logout successful. Token deleted."}, status=status.HTTP_200_OK)
    