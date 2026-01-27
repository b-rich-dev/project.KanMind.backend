from django.urls import path
from .views import EmailCheckView, BoardsView, BoardsDetailView, AssignedTasksView, ReviewingTasksView, TasksView, TaskDetailView, TaskCommentsView, TaskCommentsDetailView


urlpatterns = [
    path('boards/', BoardsView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardsDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='tasks-reviewing'),
    path('tasks/', TasksView.as_view(), name='tasks-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/', TaskCommentsView.as_view(), name='task-comments'),
    path('tasks/<int:pk>/comments/<int:comment_pk>/', TaskCommentsDetailView.as_view(), name='task-comments-detail'),
]