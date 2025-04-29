from django.urls import path
from .views import DreamView, LikeDreamView

app_name = 'dream'

urlpatterns = [

    path('dreams/<int:id>/', DreamView.as_view(), name='dream'),
    path('dreams/<int:id>/like/', LikeDreamView.as_view(), name='like_dream'),
]