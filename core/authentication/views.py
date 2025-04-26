from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view to use our enhanced serializer"""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    """View for blacklisting the refresh token on logout"""
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserDetailView(generics.RetrieveAPIView):
    """View to retrieve user details"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user