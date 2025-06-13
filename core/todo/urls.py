from django.urls import path
from .views import TodoListCreateView, TodoRetrieveUpdateDestroyView, TodoExecuteView

urlpatterns = [
    path('todo/', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todo/<int:pk>/', TodoRetrieveUpdateDestroyView.as_view(), name='todo-retrieve-update-destroy'),
    path('todo/<int:pk>/execute/', TodoExecuteView.as_view(), name='todo-execute')
]