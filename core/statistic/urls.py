
from .views import (
    UserStatisticView,
)

from django.urls import path

app_name = 'statistic'

urlpatterns = [
    path('statistics/', UserStatisticRetrieveView.as_view(), name='user_statistic_retrieve'),
]