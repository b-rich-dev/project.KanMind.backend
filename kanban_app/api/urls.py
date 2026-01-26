from django.urls import path
from .views import EmailCheckView, BoardsView, BoardsDetailView, AssignedTasksView, ReviewingTasksView, TasksView


urlpatterns = [
    path('boards/', BoardsView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardsDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='tasks-reviewing'),
    path('tasks/', TasksView.as_view(), name='tasks-list'),
]