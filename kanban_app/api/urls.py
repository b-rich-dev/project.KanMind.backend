from django.urls import path
from .views import EmailCheckView, BoardsView, BoardsDetailView


urlpatterns = [
    path('boards/', BoardsView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardsDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]