
from core.accounts.models import UserStreak
from core.accounts.settings import STREAK_REWARDS

from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class UserStreakService:
    def __init__(self, user: User):
        self.user = user
        try:
            self.streak = user.streak
        except UserStreak.DoesNotExist:
            self.create_streak()

    def get_or_create_streak(self) -> UserStreak:
        return UserStreak.objects.get_or_create(user=self.user)[0]

    def create_streak(self) -> None:
        self.streak = UserStreak.objects.create(
            user=self.user,
            current_streak=0,
            max_streak=0,
        )

    def increase_streak(self) -> None:
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        if self.streak.last_active is not None and self.streak.last_active.date() < yesterday:
            self.reset_streak()
            self.streak.last_active = timezone.now()
            self.streak.save(update_fields=['current_streak', 'last_active'])
        if self.streak.last_active is not None and self.streak.last_active.date() == yesterday:
            self.update_streak()
        
        #TODO: сделать более гибко
        if self.streak.current_streak in STREAK_REWARDS.keys():
            self._reward_streak_bonus()

    def reset_streak(self) -> None:
        self.streak.current_streak = 0

    def update_streak(self) -> None:
        self.streak.current_streak += 1
        if self.streak.current_streak > self.streak.max_streak:
            self.streak.max_streak = self.streak.current_streak

        self.streak.last_active = timezone.now()
        self.streak.save(update_fields=['current_streak', 'max_streak', 'last_active'])
    
    def _reward_streak_bonus(self) -> None:
        profile = self.user.profile
        cur_streak = self.streak.current_streak
        reward = STREAK_REWARDS.get(cur_streak, {'xp': 0, 'balance': 0})
        
        profile.xp += reward['xp']
        profile.balance += reward['balance']
        profile.save(update_fields=['xp', 'balance'])
