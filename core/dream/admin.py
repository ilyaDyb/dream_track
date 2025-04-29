from django.contrib import admin

from core.dream.models import Dream, DreamImage, DreamLike

class DreamImageInline(admin.TabularInline):
    model = DreamImage
    extra = 1
    readonly_fields = ['created_at']

class DreamLikeInline(admin.TabularInline):
    model = DreamLike
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False

@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price', 'is_active', 'created_at', 'likes_count']
    list_filter = ['category', 'is_active', 'is_private', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DreamImageInline, DreamLikeInline]

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(DreamImage)
class DreamImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'is_preview', 'created_at']
    list_filter = ['is_preview', 'created_at']
    search_fields = ['image__name']
    readonly_fields = ['created_at']

@admin.register(DreamLike)
class DreamLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'dream', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'dream__title']
    readonly_fields = ['created_at']

# Remove the direct registration since we're using the decorator
# admin.site.unregister(DreamLike)
