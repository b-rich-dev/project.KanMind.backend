from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import KanbanBoard, Task
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskDetailSerializer, TaskCommentsSerializer
from .permissions import IsBoardOwnerOrMember


class BoardsView(generics.ListCreateAPIView):
    """
    API view to list and create Kanban boards.
    
    Returns only boards owned by the current user or boards where the user is assigned to tasks.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BoardSerializer
    
    def get_queryset(self):
        """Filter boards to show only those owned by or assigned to the current user."""
        user = self.request.user
        return KanbanBoard.objects.filter(
            Q(owner=user) | Q(board_tasks__assignee=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

      
class BoardsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific Kanban board.
    
    Only board owners or members can access the board.
    """
    queryset = KanbanBoard.objects.all()
    permission_classes = [IsBoardOwnerOrMember]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        
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
    """
    API view to list and create tasks.
    
    Only board members can create tasks for that board.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        """
        Check if user is a member of the board before creating the task.
        """
        board = serializer.validated_data.get('board')
        user = self.request.user
        
        # Check if user is owner or member of the board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to create tasks.")
        
        serializer.save()
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response({"message": "The task has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    
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