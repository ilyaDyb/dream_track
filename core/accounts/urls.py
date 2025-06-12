
from django.urls import path
from .views import UserProfileView, UserProfileAvatarView

app_name = 'accounts'

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile_self'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='profile_other'),
    path('profile/avatar/', UserProfileAvatarView.as_view(), name='profile_avatar'),
]