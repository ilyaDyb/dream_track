
from django.urls import path
from .views import UserProfileView, ApplyInventoryItemView, UserInventoryView, AchievementListView, AchievementClaimView

app_name = 'accounts'

urlpatterns = [
    # profile
    path('profile/', UserProfileView.as_view(), name='profile_self'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='profile_other'),
    # path('profile/avatar/', UserProfileAvatarView.as_view(), name='profile_avatar'),

    # inventory
    path('inventory/', UserInventoryView.as_view(), name='inventory'),
    path('inventory/<int:item_id>/apply/', ApplyInventoryItemView.as_view(), name='inventory_apply'),

    # achievements
    path('achievements/', AchievementListView.as_view(), name='achievements'),
    path('achievements/<int:achievement_id>/claim/', AchievementClaimView.as_view(), name='achievement_claim'),

]