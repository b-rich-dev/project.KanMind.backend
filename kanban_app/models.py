from django.db import models
from django.contrib.auth.models import User


class KanbanBoard(models.Model):
    """
    Kanban board model for organizing tasks.
    
    A board has an owner and can have multiple members.
    Tasks are associated with boards through a foreign key relationship.
    
    Attributes:
        title: Board name
        members: Users who can access and work on the board
        created_at: Timestamp when board was created
        updated_at: Timestamp when board was last modified
        owner: User who created and owns the board
    """
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='kanban_boards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_kanban_board')

    def __str__(self):
        return self.title
       

class Task(models.Model):
    """
    Task model representing work items on a Kanban board.
    
    Tasks belong to a board and can be assigned to users for completion
    and review. Tasks track their status, priority, and due dates.
    
    Attributes:
        board: The Kanban board this task belongs to
        title: Task name
        description: Detailed task description
        status: Current task status (to_do, in_progress, review, done)
        priority: Task priority level (low, medium, high)
        assignee: User responsible for completing the task
        reviewer_id: User responsible for reviewing the task
        created_by: User who created the task
        due_date: Target completion date
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='board_tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=[('to_do', 'To Do'), ('in_progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')], default='to_do')
    priority = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned')
    reviewer_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_to_review')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created', null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    """
    Comment model for task discussions.
    
    Comments allow board members to communicate about specific tasks.
    Each comment is associated with a task and has an author.
    
    Attributes:
        task: The task this comment belongs to
        created_at: Timestamp when comment was created
        author: User who wrote the comment
        content: The comment text (max 1000 characters)
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"
    