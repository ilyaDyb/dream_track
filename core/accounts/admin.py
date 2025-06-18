from django.contrib import admin
from core.accounts.models import UserProfile, UserInventory, UserBoost, UserStreak

admin.site.register(UserProfile)
admin.site.register(UserInventory)
admin.site.register(UserBoost)
admin.site.register(UserStreak)