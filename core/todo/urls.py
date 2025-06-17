from django.urls import path
from .views import TodoListCreateView, TodoRetrieveUpdateDestroyView, TodoExecuteView

urlpatterns = [
    path('todos/', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', TodoRetrieveUpdateDestroyView.as_view(), name='todo-retrieve-update-destroy'),
    path('todos/<int:pk>/execute/', TodoExecuteView.as_view(), name='todo-execute')
]