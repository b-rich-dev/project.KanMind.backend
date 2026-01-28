from django.db import models
from django.contrib.auth.models import User

class KanbanBoard(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='kanban_boards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_kanban_board')

    def __str__(self):
        return self.title
       

class Task(models.Model):
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
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"