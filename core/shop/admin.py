from django.contrib import admin
from django.utils.html import format_html
from .models import BackgroundItem, AvatarItem, IconItem, BoostItem, BaseShopItem

@admin.register(BaseShopItem)
class BaseShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'rarity', 'price', 'is_donation_only', 'is_active', 'image_preview')
    list_filter = ('type', 'rarity', 'is_active', 'is_donation_only')
    search_fields = ('name',)
    readonly_fields = ('type',)
    ordering = ('-rarity', 'name')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 80px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Превью'

@admin.register(AvatarItem)
class AvatarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'price', 'is_active')
    list_filter = ('rarity', 'is_active')
    search_fields = ('name',)


@admin.register(BackgroundItem)
class BackgroundItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'price', 'is_active')
    list_filter = ('rarity', 'is_active')
    search_fields = ('name',)


@admin.register(IconItem)
class IconItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'price', 'is_donation_only', 'is_active')
    list_filter = ('rarity', 'is_donation_only', 'is_active')
    search_fields = ('name',)


@admin.register(BoostItem)
class BoostItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'boost_type', 'multiplier', 'duration_minutes', 'price', 'is_active')
    list_filter = ('boost_type', 'rarity', 'is_active')
    search_fields = ('name',)