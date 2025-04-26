from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from core.authentication.models import User

class Dream(models.Model):
    class DreamCategory(models.TextChoices):
        CAR = 'CAR', _('Машина')
        TRAVEL = 'TRAVEL', _('Путешествие')
        HOME = 'HOME', _('Квартира')
        OTHER = 'OTHER', _('Другое')

    user = models.ForeignKey(User, related_name='dreams', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, blank=True, null=True)
    category = models.CharField(max_length=16, choices=DreamCategory.choices, default=DreamCategory.OTHER)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
        
    class Meta:
        verbose_name = _('Мечта')
        verbose_name_plural = _('Мечты')
        unique_together = ('user', 'title')


class DreamImage(models.Model):
    dream = models.ForeignKey(Dream, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dream_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Изображение')
        verbose_name_plural = _('Изображения')

class DreamLike(models.Model):
    user = models.ForeignKey(User, related_name='dream_likes', on_delete=models.CASCADE)
    dream = models.ForeignKey(Dream, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} liked {self.dream.title}"
    
    class Meta:
        verbose_name = _('Лайк')
        verbose_name_plural = _('Лайки')
        unique_together = ('user', 'dream')
