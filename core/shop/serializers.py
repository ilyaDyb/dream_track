from rest_framework import serializers

from core.shop.models import BaseShopItem
from core.accounts.models import UserInventory


class BaseShopItemSerializer(serializers.ModelSerializer):
    is_donation_only = serializers.BooleanField(read_only=True)
    is_bought = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BaseShopItem
        fields = ['id', 'name', 'description', 'image', 'price', 'type', 'is_active', 'is_donation_only', 'is_bought']
        read_only_fields = ['id', 'is_donation_only', 'is_bought']

    def get_is_bought(self, obj):
        return UserInventory.objects.filter(user=self.context['request'].user, item=obj).exists()
        
class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseShopItem
        fields = ['id', 'name', 'description', 'image', 'price', 'type']
        