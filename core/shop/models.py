from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from core.accounts.models import UserInventory
from .interfaces import SaveableItemMixin, ApplicableItemMixin

User = get_user_model()


class BaseShopItem(models.Model):
    class RarityChoices(models.TextChoices):
        COMMON = "common"
        RARE = "rare"
        EPIC = "epic"
        LEGENDARY = "legendary"
    
    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=20, choices=RarityChoices.choices, default=RarityChoices.COMMON)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='shop_items/')
    price = models.PositiveIntegerField()
    is_donation_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    class ItemType(models.TextChoices):
        BACKGROUND = "background"
        AVATAR = "avatar"
        ICON = "icon"
        BOOST = "boost"

    type = models.CharField(max_length=20, choices=ItemType.choices)

    class Meta:
        abstract = False

    def buy_item(self, user) -> tuple[bool, str]:
        if not self.is_active:
            return False, 'Предмет не доступен'

        if self.is_donation_only:
            if self.price > user.profile.donation_balance:
                return False, 'Недостаточно кристаллов'
            user.profile.donation_balance -= self.price
        else:
            if self.price > user.profile.balance:
                return False, 'Недостаточно монет'
            user.profile.balance -= self.price
            
        with transaction.atomic():
            user.profile.save()
            UserInventory.objects.create(user=user, item=self)
            self.__update_progress()

        return True, 'Предмет успешно куплен'

    def __str__(self):
        return self.name

    def get_instance_by_type(self):
        item_class = {
            self.ItemType.BACKGROUND: BackgroundItem,
            self.ItemType.AVATAR: AvatarItem,
            self.ItemType.ICON: IconItem,
            self.ItemType.BOOST: BoostItem
        }.get(self.type)

        return item_class.objects.get(id=self.id)

    def __update_progress(self):
        UserProgressService(self.user).update_stat('items_bought')
        AchievementService(self.user).check_achievements('total_purchases', {'total_purchases': self.user.inventory.count()})

class BackgroundItem(BaseShopItem, SaveableItemMixin, ApplicableItemMixin):
    def save(self, *args, **kwargs):
        self.type = self.ItemType.BACKGROUND
        super().save(*args, **kwargs)

    def apply_to_user(self, user):
        with transaction.atomic():
            UserInventory.objects.filter(user=user, item__type=self.ItemType.BACKGROUND).update(is_equipped=False)
            UserInventory.objects.update_or_create(user=user, item=self, defaults={'is_equipped': True})

class AvatarItem(BaseShopItem, SaveableItemMixin, ApplicableItemMixin):
    def save(self, *args, **kwargs):
        self.type = self.ItemType.AVATAR
        super().save(*args, **kwargs)

    def apply_to_user(self, user):
        with transaction.atomic():
            UserInventory.objects.filter(user=user, item__type=self.ItemType.AVATAR).update(is_equipped=False)
            UserInventory.objects.update_or_create(user=user, item=self, defaults={'is_equipped': True})


class IconItem(BaseShopItem, SaveableItemMixin, ApplicableItemMixin):
    def save(self, *args, **kwargs):
        self.type = self.ItemType.ICON
        super().save(*args, **kwargs)

    def apply_to_user(self, user):
        with transaction.atomic():
            UserInventory.objects.filter(user=user, item__type=self.ItemType.ICON).update(is_equipped=False)
            UserInventory.objects.update_or_create(user=user, item=self, defaults={'is_equipped': True})

#profile frame name font / style UI skin / theme

class BoostItem(BaseShopItem, SaveableItemMixin, ApplicableItemMixin):
    class BoostType(models.TextChoices):
        XP = "xp"
        MONEY = "money"

    boost_type = models.CharField(max_length=20, choices=BoostType.choices)
    multiplier = models.FloatField(default=1.5)
    duration_minutes = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.type = self.ItemType.BOOST
        super().save(*args, **kwargs)

    def apply_to_user(self, user):
        if UserBoost.objects.filter(user=user, boost=self, expires_at__gt=timezone.now()).exists():
            raise ValueError("User already has boost")
        expires = timezone.now() + timezone.timedelta(minutes=self.duration_minutes)
        UserBoost.objects.create(user=user, boost=self, expires_at=expires)