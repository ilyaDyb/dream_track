from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    xp = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=0)
    donation_balance = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def avatar(self):
        avatar = self.get_active_items().filter(item__type='avatar').first()
        if avatar:
            return avatar.item.image.url
        from django.templatetags.static import static
        return static('shop_items/avatars/default.png')

    @property
    def level(self):
        from .leveling import get_level_by_xp
        return get_level_by_xp(self.xp)

    @property
    def background(self):
        background = self.get_active_items().filter(item__type='background').first()
        if background:
            return background.item.image.url
        from django.templatetags.static import static
        return static('shop_items/backgrounds/default.png')

    @property
    def icon(self) -> dict[str, str] | None:
        icon = self.get_active_items().filter(item__type='icon').first()
        if icon:
            return {
                'name': icon.item.name,
                'description': icon.item.description,
            }
        return None

    def get_inventory(self):
        return UserInventory.objects.filter(user=self.user)

    def get_active_items(self):
        return self.user.inventory.filter(is_equipped=True)

class UserInventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey('shop.BaseShopItem', on_delete=models.CASCADE)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f'{self.user.username} {self.item.name} {self.is_equipped}'

class UserBoost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boosts')
    boost = models.ForeignKey('shop.BoostItem', on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    def is_active(self):
        return timezone.now() < self.expires_at

class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} | Current streak: {self.current_streak} | Max streak: {self.max_streak}'


class Achievement(models.Model):
    code = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    trigger = models.CharField(max_length=100)
    condition_data = models.JSONField()
    
    reward_xp = models.PositiveIntegerField(default=0)
    reward_coins = models.PositiveIntegerField(default=0)
    reward_items = models.ManyToManyField('shop.BaseShopItem', blank=True)
    
    one_time = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    is_claimed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'achievement']
