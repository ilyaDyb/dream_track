from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    xp = models.PositiveIntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    donation_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        from django.templatetags.static import static
        return static('avatars/default.png')

    @property
    def level(self):
        from .leveling import get_level_by_xp
        return get_level_by_xp(self.xp)