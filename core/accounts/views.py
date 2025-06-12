from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.accounts.models import UserProfile
from core.accounts.serializers import UserProfileSerializer
from core.docs.templates import AUTH_HEADER


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


class UserProfileAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)

        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)

        profile.avatar = avatar
        profile.save()
        return Response({'avatar_url': profile.avatar_url}, status=status.HTTP_200_OK)
