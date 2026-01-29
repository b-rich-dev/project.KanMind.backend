from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import KanbanBoard, Task, Comment
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
        return KanbanBoard.objects.filter(Q(owner=user) | Q(board_tasks__assignee=user)).distinct()
    
    def perform_create(self, serializer):
        """Set the current user as the board owner."""
        serializer.save(owner=self.request.user)

      
class BoardsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific Kanban board.
    
    Only board owners or members can access the board.
    """
    queryset = KanbanBoard.objects.all()
    permission_classes = [IsBoardOwnerOrMember]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return BoardDetailSerializer
        
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardDetailSerializer
      
        
class EmailCheckView(APIView):
    """
    API view to check if an email address is registered.
    
    Returns user information if email exists, 404 if not found.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Check if email exists and return user data.
        
        Query parameter:
            email: The email address to check
            
        Returns:
            200: User data (id, email, fullname) if found
            404: Error message if email not found
            400: Error if email parameter missing
        """
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
    """
    API view to list all tasks assigned to the current user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Return tasks where current user is the assignee."""
        return Task.objects.filter(assignee=self.request.user)
    
    
class ReviewingTasksView(generics.ListAPIView):
    """
    API view to list all tasks where the current user is a reviewer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Return tasks where current user is the reviewer."""
        return Task.objects.filter(reviewer_id=self.request.user)
    
    
class TasksView(generics.ListCreateAPIView):
    """
    API view to list and create tasks.
    
    Only board members can create tasks for that board.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        """
        Check if board exists before validation.
        """
        board_id = request.data.get('board')
        
        # Check if board exists
        if board_id:
            board = KanbanBoard.objects.filter(id=board_id).first()
            if not board:
                return Response({"message": "Board not found. Board does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Check if user is a member of the board before creating the task.
        """
        board = serializer.validated_data.get('board')
        user = self.request.user
        
        # Check if user is owner or member of the board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to create tasks.")
        
        serializer.save(created_by=user)
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific task.
    
    Only board members can update or delete tasks.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()
    
    def perform_update(self, serializer):
        """
        Check if user is a member of the board before updating the task.
        """
        task = self.get_object()
        board = task.board
        user = self.request.user
        
        # Check if user is owner or member of the board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to update tasks.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Check if user is the task creator or board owner before deleting the task.
        """
        board = instance.board
        user = self.request.user
        
        # Only task creator or board owner can delete
        if user != instance.created_by and user != board.owner:
            raise PermissionDenied("Only the task creator or board owner can delete this task.")
        
        instance.delete()
    
    
class TaskCommentsView(generics.ListCreateAPIView):
    """
    API view to list and create comments for a specific task.
    
    Only board members can view and create comments.
    Comments are sorted chronologically by creation date.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentsSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk']
        task = get_object_or_404(Task, id=task_id)
        
        # Check if user is board member
        board = task.board
        user = self.request.user
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to view comments.")
        
        # Return comments sorted by creation date
        return task.task_comments.all().order_by('created_at')
    
    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        user = self.request.user
        
        # Check if user is board member
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to comment on tasks.")
        
        serializer.save(author=user, task=task)
    
   
class TaskCommentsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific comment.
    
    Only board members can access comments. Only the comment author can delete it.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentsSerializer
    lookup_url_kwarg = 'comment_pk'

    def get_queryset(self):
        task_id = self.kwargs['pk']
        task = get_object_or_404(Task, id=task_id)
        
        # Check if user is board member
        board = task.board
        user = self.request.user
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to access comments.")
        
        return task.task_comments.all()
    
    def perform_destroy(self, instance):
        """
        Only the comment author can delete the comment.
        """
        user = self.request.user
        
        # Check if user is the comment author
        if user != instance.author:
            raise PermissionDenied("Only the comment author can delete this comment.")
        
        instance.delete()
