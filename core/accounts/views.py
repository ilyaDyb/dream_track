from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation.trans_real import all_locale_paths
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.models import Q

from drf_yasg.utils import APIView, swagger_auto_schema
from drf_yasg import openapi

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from core.accounts.models import Achievement, UserProfile, UserInventory, Trade
from core.accounts.serializers import UserProfileSerializer, UserInventorySerializer, AchievementSerializer, TradeSerializer, CUDTradeSerializer
from core.accounts.services import UserAchievementService
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

class AchievementListView(generics.ListAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(manual_parameters=[
        AUTH_HEADER,
        openapi.Parameter('all', openapi.IN_QUERY, description='Show all achievements', type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('claimed', openapi.IN_QUERY, description='Filter by claimed status', type=openapi.TYPE_BOOLEAN),
    ])
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60*15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Achievement.objects.none()
            
        all_achievements = self.request.query_params.get('all', 'false').lower() == 'true'
        claimed = self.request.query_params.get('claimed', 'false').lower() == 'true'
    
        if all_achievements:
            return Achievement.objects.all()
        
        return Achievement.objects.filter(
            userachievement__user=self.request.user,
            userachievement__is_claimed=claimed
        )


class AchievementClaimView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        achievement_id = kwargs.get('achievement_id')
        achievement = get_object_or_404(Achievement, id=achievement_id)
        UserAchievementService(request.user).activate_achievement(achievement_id)
        return Response({'message': f"Достижение {achievement.title} успешно активировано"}, status=status.HTTP_200_OK)


class TradeListCreateView(generics.ListCreateAPIView):
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    queryset = Trade.objects.all()

    # @method_decorator(vary_on_headers('Authorization'))
    # @method_decorator(cache_page(60*15))
    @swagger_auto_schema(
        manual_parameters=[
            AUTH_HEADER,
            openapi.Parameter('all', openapi.IN_QUERY, description='Show all trades', type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('rejected', openapi.IN_QUERY, description='Filter by rejected status', type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('accepted', openapi.IN_QUERY, description='Filter by accepted status', type=openapi.TYPE_BOOLEAN),
        ],
        responses={200: TradeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        serializer = TradeSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        serializer = CUDTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trade = serializer.save(user=request.user)
        return Response({'trade': TradeSerializer(trade).data}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        rejected = self.request.query_params.get('rejected', 'false').lower() == 'true'
        accepted = self.request.query_params.get('accepted', 'false').lower() == 'true'
        all = self.request.query_params.get('all', 'false').lower() == 'true'
        base_query = Trade.objects.filter(
            Q(requester_id=self.request.user.id) | Q(recipient_id=self.request.user.id)
        ).order_by('-created_at')
        
        if all:
            return base_query
        if rejected:
            return base_query.filter(status=Trade.Status.REJECTED)
        if accepted:
            return base_query.filter(status=Trade.Status.ACCEPTED)
        return base_query


class TradeAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        trade_id = kwargs.get('trade_id')
        trade = get_object_or_404(Trade, id=trade_id)
        trade.accept_trade(request.user)
        return Response({'message': f"Сделка {trade.id} успешно принята"}, status=status.HTTP_200_OK)


class TradeRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        trade_id = kwargs.get('trade_id')
        trade = get_object_or_404(Trade, id=trade_id)
        trade.reject_trade(request.user)
        return Response({'message': f"Сделка {trade.id} успешно отклонена"}, status=status.HTTP_200_OK)
    