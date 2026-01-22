from django.urls import path, include

urlpatterns = [
    path('', include('kanban_app.api.urls')),
]
