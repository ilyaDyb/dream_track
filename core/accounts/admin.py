from django.contrib import admin
from core.accounts.models import UserProfile, UserInventory, UserBoost

admin.site.register(UserProfile)
admin.site.register(UserInventory)
admin.site.register(UserBoost)