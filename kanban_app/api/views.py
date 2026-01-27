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
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskDetailSerializer, TaskCommentsSerializer
from kanban_app.models import KanbanBoard, Task


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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "The board has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
      
        
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
        
        
class AssignedTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)
    
    
class ReviewingTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer_id=self.request.user)
    
    
class TasksView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "The task has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    
class TaskCommentsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentsSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk']
        return Task.objects.filter(id=task_id).first().task_comments.all()
    
    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)
    
   
class TaskCommentsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentsSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk']
        return Task.objects.filter(id=task_id).first().task_comments.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "The comment has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT) 