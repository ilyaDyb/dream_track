from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.urls import reverse

from core.accounts.validators import validate_trade_offer


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

    def get_absolute_url(self):
        return reverse('accounts:profile_other', kwargs={'pk': self.user.id})

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


class Trade(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requester_trades')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_trades')
    requester_offer = models.JSONField(default=dict, validators=[validate_trade_offer], help_text='Trade offer | Example: {"coins": 100, "items_ids": [1, 2, 3]}')
    recipient_offer = models.JSONField(default=dict, validators=[validate_trade_offer], help_text='Trade offer | Example: {"coins": 100, "items_ids": [1, 2, 3]}')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.requester == self.recipient:
            raise ValidationError("Requester and recipient cannot be the same")
        
        if not any([
            self.requester_offer.get('coins'),
            self.requester_offer.get('items_ids')
        ]):
            raise ValidationError("Requester trade offer must contain coins or items")
            
        if not any([
            self.recipient_offer.get('coins'),
            self.recipient_offer.get('items_ids')
        ]):
            raise ValidationError("Recipient trade offer must contain  coins or items")

        if 'items_ids' in self.requester_offer or 'items_ids' in self.recipient_offer:
            self._check_items_ids()
    
    def _check_items_ids(self):
        requester_items_ids = self.requester_offer.get('items_ids', [])
        recipient_items_ids = self.recipient_offer.get('items_ids', [])

        if set(requester_items_ids) & set(recipient_items_ids):
            raise ValidationError("Same item(s) cannot be traded by both sides")

        if requester_items_ids:
            requester_items = UserInventory.objects.filter(
                user=self.requester, 
                id__in=requester_items_ids
            )
            print(requester_items, requester_items_ids)
            if len(requester_items) != len(requester_items_ids):
                raise ValidationError("Requester doesn't own all the items in the trade offer")
        
        if recipient_items_ids:
            recipient_items = UserInventory.objects.filter(
                user=self.recipient, 
                id__in=recipient_items_ids
            )
            if len(recipient_items) != len(recipient_items_ids):
                raise ValidationError("Recipient doesn't own all the items in the trade offer")
    
    def accept_trade(self, user):
        if user != self.requester and user != self.recipient:
            raise ValidationError("User is not involved in this trade")
        
        if user != self.recipient:
            raise ValidationError("User is not the recipient of this trade")

        if self.status != self.Status.PENDING:
            raise ValidationError("Trade is not in pending state")

        with transaction.atomic():      
            if 'coins' in self.requester_offer:
                if self.requester.profile.balance < self.requester_offer['coins']:
                    raise ValidationError("Requester doesn't have enough coins")
                self.requester.profile.balance -= self.requester_offer['coins']
                self.recipient.profile.balance += self.requester_offer['coins']
            
            if 'coins' in self.recipient_offer:
                if self.recipient.profile.balance < self.recipient_offer['coins']:
                    raise ValidationError("Recipient doesn't have enough coins")
                self.recipient.profile.balance -= self.recipient_offer['coins']
                self.requester.profile.balance += self.recipient_offer['coins']

            if 'items_ids' in self.requester_offer:
                items_to_recipient = []
                for item_id in self.requester_offer['items_ids']:
                    item = UserInventory.objects.get(id=item_id, user=self.requester)
                    items_to_recipient.append(item)
                    item.delete()
                
                for item in items_to_recipient:
                    item.user = self.recipient
                    item.save()

            if 'items_ids' in self.recipient_offer:
                items_to_requester = []
                for item_id in self.recipient_offer['items_ids']:
                    item = UserInventory.objects.get(id=item_id, user=self.recipient)
                    items_to_requester.append(item)
                    item.delete()
                
                for item in items_to_requester:
                    item.user = self.requester
                    item.save()

            self.requester.profile.save()
            self.recipient.profile.save()
            
            # Update trade status
            self.status = self.Status.ACCEPTED
            self.save()
    
    def reject_trade(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("Trade is not in pending state")
        self.status = self.Status.REJECTED
        self.save()
    
    def __str__(self):
        return f"Trade {self.id}: {self.requester.username} <-> {self.recipient.username} ({self.status})"
    
    class Meta:
        verbose_name = 'Обмен'
        verbose_name_plural = 'Обмены'
        ordering = ['-created_at']

class FriendRelation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_user_friends(cls, user: User, status: str):
        if status not in ['pending', 'accepted', 'rejected']:
            raise ValueError("Invalid status")

        with transaction.atomic():
            friends = cls.objects.filter(
                Q(requester=user) | Q(recipient=user),
                status=status
            )
            return [friend.requester if friend.requester != user else friend.recipient for friend in friends]

    def accept_friend_request(self, user: User):
        if user != self.requester and user != self.recipient:
            raise ValidationError("User is not the requester or recipient of the friend request")
        if user != self.recipient:
            raise ValidationError("User is not the recipient of the friend request")
        if self.status != self.Status.PENDING:
            raise ValidationError("Friend request is not in pending state")
        self.status = self.Status.ACCEPTED
        self.save()

    def reject_friend_request(self, user: User):
        if user != self.requester and user != self.recipient:
            raise ValidationError("User is not the requester or recipient of the friend request")
        if self.status != self.Status.PENDING:
            raise ValidationError("Friend request is not in pending state")
        if user != self.requester:
            raise ValidationError("User is not the requester of the friend request")
        self.status = self.Status.REJECTED
        self.save()

    @classmethod
    def get_pending_friend_requests(cls, user: User, as_requester: bool = False):
        if as_requester:
            return cls.objects.filter(
                requester=user,
                status=cls.Status.PENDING
            )
        return cls.objects.filter(
            recipient=user,
            status=cls.Status.PENDING
        )

    @classmethod
    def make_friend_request(cls, requester: User, recipient: User):
        if requester == recipient:
            raise ValidationError("User cannot make a friend request to himself")
        if cls.objects.filter(
                Q(requester=requester, recipient=recipient) | Q(requester=recipient, recipient=requester)
            ):
            raise ValidationError("Friend request already exists")

        with transaction.atomic():
            cls.objects.create(
                requester=requester,
                recipient=recipient,
                status=cls.Status.PENDING
            )

    def __str__(self):
        return f"Friend request {self.id}: {self.requester.username} <-> {self.recipient.username} ({self.status})"

class UserDailyRoulette(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_roulette')
    last_spin = models.DateTimeField(null=True, blank=True)