from rest_framework import generics

from drf_yasg.utils import swagger_auto_schema

from core.accounts.settings import AUTH_HEADER
from core.statistic.models import Statistic

from django.db.models import get_or_create


class UserStatisticRetrieveView(generics.RetrieveAPIView):

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_object(self):
        statistic = get_or_create(Statistic, user=self.request.user)[0]
        return statistic
