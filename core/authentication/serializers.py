from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    avatar = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()

    def get_profile_url(self, obj):
        if obj.profile:
            return reverse('accounts:profile_other', kwargs={'pk': obj.id})
        return ''


    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'profile_url')
        read_only_fields = ('id',)

    def get_avatar(self, obj):
        return obj.profile.avatar
    
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for creating user accounts"""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'username': {'required': True},
            'password': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user details in response"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        return data


class LogoutSerializer(serializers.Serializer):
    """Serializer for the logout endpoint"""
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            raise serializers.ValidationError(str(e))

