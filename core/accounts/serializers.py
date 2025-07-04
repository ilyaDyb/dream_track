from rest_framework import serializers

from core.accounts.services import UserStreakService
from core.shop.models import BaseShopItem, BoostItem, AvatarItem, BackgroundItem, IconItem
from core.accounts.models import Achievement, UserProfile, UserInventory


# Profile
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    level = serializers.IntegerField(read_only=True)
    streak = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'avatar', 'background',
            'icon', 'xp', 'level', 'balance', 'donation_balance', 'streak'
        ]
        read_only_fields = ['id', 'xp', 'level', 'balance', 'donation_balance', 'streak']

    def get_streak(self, obj):
        streak = UserStreakService(obj.user).get_or_create_streak()
        return {
            'current_streak': streak.current_streak,
            'max_streak': streak.max_streak,
            'last_active': streak.last_active
        }

# Inventory
class BaseShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseShopItem
        fields = ['id', 'name', 'description', 'image', 'price', 'type', 'rarity', 'is_donation_only', 'is_active']

class BoostItemSerializer(BaseShopItemSerializer):
    class Meta(BaseShopItemSerializer.Meta):
        model = BoostItem
        fields = BaseShopItemSerializer.Meta.fields + ['boost_type', 'multiplier', 'duration_minutes']

class AvatarItemSerializer(BaseShopItemSerializer):
    class Meta(BaseShopItemSerializer.Meta):
        model = AvatarItem

class BackgroundItemSerializer(BaseShopItemSerializer):
    class Meta(BaseShopItemSerializer.Meta):
        model = BackgroundItem

class IconItemSerializer(BaseShopItemSerializer):
    class Meta(BaseShopItemSerializer.Meta):
        model = IconItem

class PolymorphicItemField(serializers.Field):
    def to_representation(self, obj):
        item_type = getattr(obj, 'type', None)
        if item_type == 'boost':
            return BoostItemSerializer(BoostItem.objects.get(id=obj.id)).data
        elif item_type == 'avatar':
            return AvatarItemSerializer(AvatarItem.objects.get(id=obj.id)).data
        elif item_type == 'background':
            return BackgroundItemSerializer(BackgroundItem.objects.get(id=obj.id)).data
        elif item_type == 'icon':
            return IconItemSerializer(IconItem.objects.get(id=obj.id)).data
        return BaseShopItemSerializer(obj).data


class UserInventorySerializer(serializers.ModelSerializer):
    item = PolymorphicItemField(read_only=True)
    class Meta:
        model = UserInventory
        fields = ['id', 'user', 'item', 'is_equipped']
        read_only_fields = ['id']


# Achievements
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        exclude = ['code', 'trigger', 'condition_data']