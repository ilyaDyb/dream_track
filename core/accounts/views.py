from django.shortcuts import get_object_or_404

from drf_yasg.utils import APIView, swagger_auto_schema
from drf_yasg import openapi

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from core.accounts.models import UserProfile, UserInventory
from core.accounts.serializers import UserProfileSerializer, UserInventorySerializer
from core.shop.models import BaseShopItem
from core.docs.templates import AUTH_HEADER
from core.utils.paginator import CustomPageNumberPagination

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    http_method_names = ['get']

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None

        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return get_object_or_404(self.get_queryset(), pk=pk)
        return get_object_or_404(self.get_queryset(), user=self.request.user)

class UserInventoryView(generics.ListAPIView):
    serializer_class = UserInventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    http_method_names = ['get']

    @swagger_auto_schema(manual_parameters=[
        AUTH_HEADER,
        openapi.Parameter('page', openapi.IN_QUERY, description='Page number', type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description='Number of results per page', type=openapi.TYPE_INTEGER)
    ])
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.inventory.all()

class ApplyInventoryItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        item = get_object_or_404(UserInventory, id=item_id).item.get_instance_by_type()
        item.apply_to_user(user=request.user)
        
        return Response({'message': f"Предмет {item.name} успешно применен"}, status=status.HTTP_200_OK)


# class UserProfileAvatarView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
#     def post(self, request):
#         profile = get_object_or_404(UserProfile, user=request.user)

#         avatar = request.FILES.get('avatar')
#         if not avatar:
#             return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)

#         profile.avatar = avatar
#         profile.save()
#         return Response({'avatar_url': profile.avatar_url}, status=status.HTTP_200_OK)
