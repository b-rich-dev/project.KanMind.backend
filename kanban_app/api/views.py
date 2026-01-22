from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
#from user_auth_app.models import UserProfile
#from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer
from kanban_app.models import KanbanBoard


class BoardsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = KanbanBoard.objects.all()
    serializer_class = BoardSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

      
class BoardsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = KanbanBoard.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardDetailSerializer
      
        
# View to check if an email is already registered.
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        exists = user is not None
        
        if exists:
            return Response({
                "id": user.id,
                "email": email,
                "fullname": f"{user.first_name} {user.last_name}".strip()
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email not found. The email address does not exist."}, status=status.HTTP_404_NOT_FOUND)