from django.urls import path
from .views import DreamView, LikeDreamView, DreamListView, PublicDreamListView

app_name = 'dream'

urlpatterns = [
    path('dreams/', DreamListView.as_view(), name='dreams'),
    path('dreams/public/', PublicDreamListView.as_view(), name='public_dreams'),
    path('dreams/<int:id>/', DreamView.as_view(), name='dream'),
    path('dreams/<int:id>/like/', LikeDreamView.as_view(), name='like_dream'),
]