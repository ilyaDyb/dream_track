from django.urls import path
from .views import (
    TodoListCreateView, TodoRetrieveUpdateDestroyView, TodoExecuteView,
    HabitListCreateView, HabitRetrieveUpdateDestroyView, HabitExecuteView
)

urlpatterns = [
    # Todo
    path('todos/', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', TodoRetrieveUpdateDestroyView.as_view(), name='todo-retrieve-update-destroy'),
    path('todos/<int:pk>/execute/', TodoExecuteView.as_view(), name='todo-execute'),
    
    # Habit
    path('habits/', HabitListCreateView.as_view(), name='habit-list-create'),
    path('habits/<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='habit-retrieve-update-destroy'),
    path('habits/<int:pk>/execute/', HabitExecuteView.as_view(), name='habit-execute')
]
