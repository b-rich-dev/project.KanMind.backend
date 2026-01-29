from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import KanbanBoard, Task
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskDetailSerializer, TaskCommentsSerializer
from .permissions import IsBoardOwnerOrMember, IsTaskBoardMember, IsCommentBoardMember


class BoardsView(generics.ListCreateAPIView):
    """
    API view to list and create Kanban boards.
    Returns only boards owned by the current user or boards where the user is assigned to tasks.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BoardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return KanbanBoard.objects.filter(Q(owner=user) | Q(board_tasks__assignee=user)).distinct()
    
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
      
        
class EmailCheckView(APIView):
    """
    API view to check if an email address is registered.   
    Returns user information if email exists, 404 if not found.
    """
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
    """
    API view to list all tasks assigned to the current user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)
    
    
class ReviewingTasksView(generics.ListAPIView):
    """
    API view to list all tasks where the current user is a reviewer.
    """
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

    def create(self, request, *args, **kwargs):
        """
        Check if board exists before validation.
        """
        board_id = request.data.get('board')
        
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
        
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to create tasks.")
        
        serializer.save(created_by=user)
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific task.   
    Only board members can access. Only task creator or board owner can delete.
    """
    permission_classes = [IsTaskBoardMember]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()
    
    
class TaskCommentsView(generics.ListCreateAPIView):
    """
    API view to list and create comments for a specific task.   
    Only board members can view and create comments.
    Comments are sorted chronologically by creation date.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentsSerializer

    def get_task_and_check_membership(self):
        """
        Helper method to get task and verify user is a board member.      
        Returns:
            Task: The task instance if user is a board member           
        Raises:
            Http404: If task does not exist
            PermissionDenied: If user is not a board member
        """
        task_id = self.kwargs['pk']
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        user = self.request.user
        
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to access task comments.")
        
        return task

    def get_queryset(self):
        task = self.get_task_and_check_membership()
        return task.task_comments.all().order_by('created_at')
    
    def perform_create(self, serializer):
        task = self.get_task_and_check_membership()
        serializer.save(author=self.request.user, task=task)
    
   
class TaskCommentsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific comment.  
    Only board members can access comments. Only the comment author can delete it.
    """
    permission_classes = [IsCommentBoardMember]
    serializer_class = TaskCommentsSerializer
    lookup_url_kwarg = 'comment_pk'

    def get_queryset(self):
        task_id = self.kwargs['pk']
        task = get_object_or_404(Task, id=task_id)
        return task.task_comments.all()
