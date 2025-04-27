from django.urls import path
from .views import DreamView

app_name = 'dream'

urlpatterns = [

    path('dreams/<int:pk>/', DreamView.as_view(), name='dream'),
]