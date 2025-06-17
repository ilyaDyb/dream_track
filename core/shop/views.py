from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions

from django.shortcuts import get_object_or_404

from core.docs.templates import AUTH_HEADER
from core.shop.serializers import BaseShopItemSerializer
from core.shop.models import BaseShopItem
from core.accounts.models import UserInventory
from core.utils.paginator import CustomPageNumberPagination

from django.db.models import Exists, OuterRef

"""
Common		120-180
Rare		350-500
Epic		700-1000
Legendary	Донат
"""

class ShopView(generics.ListAPIView):
    serializer_class = BaseShopItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        manual_parameters=[
            AUTH_HEADER,
            openapi.Parameter('page_size', openapi.IN_QUERY, description='Number of results per page', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('type', openapi.IN_QUERY, description="Фильтрация по типу", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('search', openapi.IN_QUERY, description="Поиск предметов по названию", type=openapi.TYPE_STRING, required=False)
        ]
    )
    def get(self,request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        query = BaseShopItem.objects.filter(is_active=True)
        if type:
            if type in BaseShopItem.ItemType.values:
                query = query.filter(type=type)
        if search:
            query = query.filter(name__icontains=search)
        # query = query.annotate(is_bought=Exists(UserInventory.objects.filter(user=self.request.user, item=OuterRef('pk'))))
        return query


class BuyShopItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        item = get_object_or_404(BaseShopItem, id=item_id)
        success, message = item.buy_item(request.user)
        if not success:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': message}, status=status.HTTP_200_OK)