from django.contrib import admin

from core.accounts import models

# Register your models here.
admin.site.register(models.UserProfile)