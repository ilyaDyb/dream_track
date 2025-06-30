from django.contrib import admin
from core.accounts.models import UserProfile, UserInventory, UserBoost, UserStreak, Achievement

admin.site.register(UserProfile)
admin.site.register(UserInventory)
admin.site.register(UserBoost)
admin.site.register(UserStreak)
admin.site.register(Achievement)