import random

from typing import List

from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

import random
from typing import List
from django.db import transaction
from core.accounts.models import UserInventory
from core.shop.models import BaseShopItem
from core.accounts.models import UserDailyRoulette
class Roulette:
    REWARDS: List[dict] = []

    @classmethod
    def spin_wheel(cls) -> dict:
        """
        Возвращает одну награду из списка REWARDS с учётом весов.
        """
        choices = cls.REWARDS
        weights = [reward["weight"] for reward in cls.REWARDS]

        return random.choices(choices, weights=weights, k=1)[0]

    @classmethod
    def get_rewards_list(cls) -> List[dict]:
        return cls.REWARDS
    
    @classmethod
    def _get_reward_to_user(cls, user: User, reward: dict) -> None:
        with transaction.atomic():
            if reward['type'] == 'coins':
                user.profile.balance += reward['amount']
                user.profile.save(update_fields=['balance'])

            elif reward['type'] == 'item':
                try:
                    item = BaseShopItem.objects.get(id=reward['item_id'])
                    UserInventory.objects.create(user=user, item=item)
                except BaseShopItem.DoesNotExist:
                    raise ValueError(f"Item with id {reward['item_id']} not found")

            else:
                raise ValueError(f"Invalid reward type: {reward['type']}")
    
    def _get_or_create_daily_roulette(self, user: User) -> UserDailyRoulette:
        daily_roulette, _ = UserDailyRoulette.objects.get_or_create(user=user)
        return daily_roulette

    def _check_available_to_spin(self, user: User) -> bool:
        daily_roulette = self._get_or_create_daily_roulette(user)
        if daily_roulette.last_spin and daily_roulette.last_spin + timezone.timedelta(days=1) > timezone.now():
            return False
        return True

    def _update_last_spin(self, user: User) -> None:
        daily_roulette = self._get_or_create_daily_roulette(user)
        daily_roulette.last_spin = timezone.now()
        daily_roulette.save(update_fields=['last_spin'])


    def spin(self, user: User) -> dict:
        if not self._check_available_to_spin(user):
            raise ValueError("User is not allowed to spin the wheel")
        with transaction.atomic():
            reward = self.spin_wheel()
            self._get_reward_to_user(user, reward)
            self._update_last_spin(user)
        return reward

class DailyRoulette(Roulette):
    REWARDS = [
        {"name": "15 coins", "type": "coins", "amount": 15, "weight": 100},
        {"name": "50 coins", "type": "coins", "amount": 50, "weight": 50},
        {"name": "100 coins", "type": "coins", "amount": 100, "weight": 10},
        {"name": "200 coins", "type": "coins", "amount": 200, "weight": 5},
        {"name": "500 coins", "type": "coins", "amount": 500, "weight": 3},
        {"name": "1000 coins", "type": "coins", "amount": 1000, "weight": 1},
        {"name": "⭐ Wishful Star: Icon", "type": "item", "item_id": 46, "weight": 0.5},
    ]


