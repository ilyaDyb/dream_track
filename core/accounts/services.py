
from core.accounts.models import UserStreak
from core.accounts.settings import STREAK_REWARDS
from core.accounts.models import Achievement, UserAchievement, UserInventory
from core.accounts.progress import UserActionProgressService

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

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
        uaps = UserActionProgressService(user=self.user)
        uaps.update_streak()

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


class AchievementService:
    AVAILIBLE_TRIGGERS = [
        'streak_updated',
        'task_completed',
        'task_failed',
        'dream_completed',
        'item_bought',
        'item_equipped',
        'total_purchases'
    ]

    def __init__(self, user):
        self.user = user

    def check_achievements(self, trigger: str, payload: dict):
        if trigger not in self.AVAILIBLE_TRIGGERS:
            raise ValueError(f"Invalid trigger: {trigger}")
        achievements = Achievement.objects.filter(trigger=trigger)
        for achievement in achievements:
            if UserAchievement.objects.filter(user=self.user, achievement=achievement).exists():
                continue

            if self._check_condition(achievement.condition_data, payload):
                self._give_achievement(achievement)
    
    def _check_condition(self, condition, payload):
        for key, value in condition.items():
            if key not in payload or payload[key] < value:
                return False
        return True

    def _give_achievement(self, achievement):
        with transaction.atomic():
            UserAchievement.objects.create(user=self.user, achievement=achievement)

class UserAchievementService:
    def __init__(self, user):
        self.user = user
        
    def activate_achievement(self, achievement_id):
        achievement = Achievement.objects.get(id=achievement_id)
        
        with transaction.atomic():
            user_achievement = UserAchievement.objects.filter(
                user=self.user, 
                achievement=achievement,
                is_claimed=False
            ).first()
            
            if not user_achievement:
                return
                
            self._reward_benefits(achievement)
            self._update_user_achievement(user_achievement)
            
    def _reward_benefits(self, achievement):
        profile = self.user.profile
        profile.xp += achievement.reward_xp
        profile.balance += achievement.reward_coins
        profile.save(update_fields=['xp', 'balance'])

        for item in achievement.reward_items.all():
            UserInventory.objects.create(user=self.user, item=item)

    def _update_user_achievement(self, user_achievement):
        user_achievement.is_claimed = True
        user_achievement.save(update_fields=['is_claimed'])

