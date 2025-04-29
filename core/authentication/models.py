from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

class User(AbstractUser):

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        from django.templatetags.static import static
        return static('avatars/default.png')

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
#TODO вынести валидацию изображений из сервиса Dream и исползовать его для автаарки
# /static/avatars/default.png