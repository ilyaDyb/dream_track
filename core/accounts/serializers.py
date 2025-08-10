from rest_framework import serializers

from django.contrib.auth import get_user_model

from core.accounts.services import UserStreakService
from core.shop.models import BaseShopItem, BoostItem, AvatarItem, BackgroundItem, IconItem
from core.accounts.models import Achievement, Trade, UserProfile, UserInventory
from core.shop.serializers import ShopItemSerializer

User = get_user_model()

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


# Trades

class CUDTradeSerializer(serializers.ModelSerializer):
    requester = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Trade
        fields = [
            'id', 'requester', 'recipient',
            'requester_offer', 'recipient_offer',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def create(self, validated_data):
        user = validated_data.pop("user", None)
        if user and "requester" not in validated_data:
            validated_data["requester"] = user
            
        requester_offer = validated_data.get("requester_offer", {})
        recipient_offer = validated_data.get("recipient_offer", {})

        def attach_items_data(user, offer):
            items_ids = offer.get("items_ids", [])
            inventories = UserInventory.objects.filter(user=user, id__in=items_ids)
            items = [inv.item.get_instance_by_type() for inv in inventories]
            offer["items_data"] = ShopItemSerializer(items, many=True).data
            return offer

        validated_data["requester_offer"] = attach_items_data(validated_data["requester"], requester_offer)
        validated_data["recipient_offer"] = attach_items_data(validated_data["recipient"], recipient_offer)

        return super().create(validated_data)



class TradeSerializer(serializers.ModelSerializer):
    requester = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    requester_offer = serializers.SerializerMethodField()
    recipient_offer = serializers.SerializerMethodField()
    class Meta:
        model = Trade
        fields = ['id', 'requester', 'recipient', 'requester_offer', 'recipient_offer', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def get_requester(self, obj):
        return dict(username=obj.requester.username, id=obj.requester.id, avatar=obj.requester.profile.avatar)

    def get_recipient(self, obj):
        return dict(username=obj.recipient.username, id=obj.recipient.id, avatar=obj.recipient.profile.avatar)

    def get_requester_offer(self, obj):
        offer = obj.requester_offer
        if 'items_data' in offer:
            return offer

        items_ids = offer.get('items_ids', [])
        inventories = UserInventory.objects.filter(id__in=items_ids)
        items = [inv.item.get_instance_by_type() for inv in inventories]
        offer["items"] = ShopItemSerializer(items, many=True).data
        return offer

    def get_recipient_offer(self, obj):
        offer = obj.recipient_offer
        if 'items_data' in offer:
            return offer

        items_ids = offer.get('items_ids', [])
        inventories = UserInventory.objects.filter(id__in=items_ids)
        items = [inv.item.get_instance_by_type() for inv in inventories]
        offer["items"] = ShopItemSerializer(items, many=True).data
        return offer