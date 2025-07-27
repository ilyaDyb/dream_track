from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

User = get_user_model()

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

    def get_dream_with_images(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': str(self.price),
            'is_private': self.is_private,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user': self.user.id,
            'images': [
                {
                    'id': image.id,
                    'image_url': image.image.url,
                    'is_preview': image.is_preview,
                    'created_at': image.created_at.isoformat()
                }
                for image in self.images.all()
            ],
            'likes_count': self.likes.count(),
            'percentage_achieved': self._get_percentage_achieved()
        }


    def _get_percentage_achieved(self):
        total_steps = self.user.todos.filter(is_dream_step=True, dream=self).count()
        completed_steps = self.user.todos.filter(is_dream_step=True, is_completed=True, dream=self).count()
        return round((completed_steps / total_steps) * 100, 2) if total_steps > 0 else 0


    def _achieve(self):
        self.is_active = False
        self.save()
        self.__update_progress()

    def __update_progress(self):
        UserProgressService(self.user).update_stat('dreams_completed')

    class Meta:
        verbose_name = _('Мечта')
        verbose_name_plural = _('Мечты')
        unique_together = ('user', 'title')


class DreamImage(models.Model):
    dream = models.ForeignKey(Dream, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dream_images/')
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dream.title} - {self.image.name}"

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
