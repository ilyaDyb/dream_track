from rest_framework import serializers

from core.accounts.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    level = serializers.IntegerField(read_only=True)
    avatar_url = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'avatar', 'avatar_url',
            'bio', 'xp', 'level', 'balance', 'donation_balance'
        ]
        read_only_fields = ['id', 'xp', 'level', 'bala']

    