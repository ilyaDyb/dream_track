from django.contrib import admin

from core.todo.models import Todo, Habit

# Register your models here.
admin.site.register(Todo)
admin.site.register(Habit)