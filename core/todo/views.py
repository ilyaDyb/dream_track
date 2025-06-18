from rest_framework import generics
from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.todo.models import Todo
from core.todo.serializers import TodoSerializer
from core.docs.templates import AUTH_HEADER


class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Todo.objects.none()
        return self._filter_queryset_by_params(Todo.objects.all()) 

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER,
            openapi.Parameter(
                'completed',
                openapi.IN_QUERY,
                description='Фильтрация по статусу завершённости: true или false',
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'expired',
                openapi.IN_QUERY,
                description='Фильтрация по просроченности (deadline < сегодня): true или false',
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'order_by',
                openapi.IN_QUERY,
                description='Поле сортировки, например: -created_at, deadline',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Номер страницы пагинации',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _filter_queryset_by_params(self, queryset):
        completed = self.request.query_params.get('completed', 'false').lower() == 'true'
        order_by = self.request.query_params.get('order_by', '-created_at')
        expired = self.request.query_params.get('expired', None)
        expired = expired == 'true' if expired else None
        queryset = queryset.filter(user=self.request.user, is_completed=completed)

        if expired is not None:
            now = timezone.now().date()
            if expired:
                queryset = queryset.filter(deadline__lt=now)
            else:
                queryset = queryset.filter(deadline__gte=now)
        
        return queryset.order_by(order_by)



class TodoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Todo.objects.none()
        return Todo.objects.filter(user=self.request.user)


class ExecuteThrottle(UserRateThrottle):
    rate = '30/day'

class TodoExecuteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ExecuteThrottle]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, pk):
        todo = generics.get_object_or_404(Todo, pk=pk, user=request.user)
        if todo.is_completed:
            return Response({"error": "Task is already completed"}, status=status.HTTP_400_BAD_REQUEST)
        xp, coins = todo.execute_task()
        return Response({"xp": xp, "coins": coins}, status=status.HTTP_200_OK)
