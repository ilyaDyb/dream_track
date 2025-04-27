from rest_framework import generics, mixins, permissions
from core.dream.models import Dream
from core.dream.serializers import DreamCUDSerializer, DreamSerializer

class DreamView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                generics.GenericAPIView):
    queryset = Dream.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'DELETE', 'PATCH']:
            return DreamCUDSerializer
        return DreamSerializer