
from django.urls import path
from .views import (UserProfileView, ApplyInventoryItemView, UserInventoryView, AchievementListView,
    AchievementClaimView, TradeListCreateView, TradeAcceptView, TradeRejectView, FriendsList,
    AcceptFriendRequest, RejectFriendRequest, MakeFriendRequest, DailyRouletteView)

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

    # trades
    path('trades/', TradeListCreateView.as_view(), name='trade_list_create'),
    path('trades/<int:trade_id>/accept/', TradeAcceptView.as_view(), name='trade_accept'),
    path('trades/<int:trade_id>/reject/', TradeRejectView.as_view(), name='trade_reject'),

    # friends
    path('friends/', FriendsList.as_view(), name='friends_list'),
    path('friends/<int:user_id>/add/', MakeFriendRequest.as_view(), name='make_friend_request'),
    path('friends/<int:friend_request_id>/accept/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    path('friends/<int:friend_request_id>/reject/', RejectFriendRequest.as_view(), name='reject_friend_request'),

    # roulettes
    path('daily_roulette/', DailyRouletteView.as_view(), name='daily_roulette'),
    
]