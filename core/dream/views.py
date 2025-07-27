from rest_framework import generics, mixins, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from core.docs.templates import AUTH_HEADER
from core.dream.models import Dream
from core.dream.serializers import DreamCUDSerializer, DreamSerializer
from core.dream.services import DreamService, DreamStepService
from core.utils.paginator import CustomPageNumberPagination
from core.todo.models import Todo
from core.todo.serializers import TodoSerializer


class DreamView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                generics.GenericAPIView):
    queryset = Dream.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'DELETE', 'PATCH']:
            return DreamCUDSerializer
        return DreamSerializer

class DreamListView(generics.ListAPIView):
    serializer_class = DreamSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Dream.objects.none()
        
        return Dream.objects.filter(user=self.request.user)

class PublicDreamListView(generics.ListAPIView):
    serializer_class = DreamSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Dream.objects.none()
        
        return Dream.objects.filter(is_private=False)

class LikeDreamView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        dream_id = kwargs.get('id')
        try:
            dream = Dream.objects.get(id=dream_id)
        except Dream.DoesNotExist:
            return Response({'error': 'Dream not found'}, status=status.HTTP_404_NOT_FOUND)
        message, status = DreamService.create_or_delete_like(dream, request.user)
        return Response({'message': message}, status=status)

# DreamSteps

class DreamStepListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TodoSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Todo.objects.none()
        
        return Todo.objects.filter(
            user=self.request.user,
            is_completed=False,
            is_dream_step=True
        )

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(is_dream_step=True)


class DreamStepRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получает, обновляет или удаляет шаг к мечте
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TodoSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Todo.objects.none()
        
        return Todo.objects.filter(
            user=self.request.user,
            is_completed=False,
            is_dream_step=True
        )
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class DreamStepExecuteView(APIView):
    """
    Выполняет шаг к мечте
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        todo_id = kwargs.get('id')
        todo_obj = Todo.objects.get(id=todo_id)
        DreamStepService.execute_dream_step(todo_obj)
        return Response({'message': 'Step executed successfully'}, status=status.HTTP_200_OK)

class DreamStepGenerateView(APIView):
    """
    Генерирует шаги к мечте на основе ИИ и возвращает их
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        dream_id = kwargs.get('dream_id')
        try:
            dream_obj = Dream.objects.get(id=dream_id)
        except Dream.DoesNotExist:
            return Response({'error': 'Dream not found'}, status=status.HTTP_404_NOT_FOUND)
        steps = DreamStepService(dream_obj).generate_steps()
        return Response({'steps': steps}, status=status.HTTP_200_OK)

class DreamStepDumbCreateView(APIView):
    """
    Принимает список шагов к мечте и создает их
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        steps = request.data.get('steps', [])
        
        if not steps:
            return Response({'error': 'Steps are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(steps, list):
            return Response({'error': 'Steps must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        if not all(isinstance(step, dict) and 'title' in step and 'difficulty' in step for step in steps):
            return Response({'error': 'Steps must be a list of dictionaries with title and difficulty'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            dream_id = kwargs.get('dream_id')
            dream_obj = Dream.objects.get(id=dream_id)
        except Dream.DoesNotExist:
            return Response({'error': 'Dream not found'}, status=status.HTTP_404_NOT_FOUND)
        DreamStepService(dream_obj).dumb_create_steps(steps)
        return Response({'message': 'Steps created successfully'}, status=status.HTTP_201_CREATED)
