
from core.accounts.models import User

class UserActionProgressService:
    def __init__(self, user: User) -> None:
        self.user = user
        self.stat = user.statistic
        self.profile = user.profile

    
    def _check_achievements(self, trigger, payload):
        from core.accounts.services import AchievementService
        AchievementService(self.user).check_achievements(trigger, payload)
    
    def update_stat(self, key, value=1, payload=None):
        from core.accounts.services import AchievementService
        stat = self.user.statistic
        new_value = getattr(stat, key) + value
        setattr(stat, key, new_value)
        stat.save(update_fields=[key])

        payload = payload or {key: new_value}
        AchievementService(self.user).check_achievements(key, payload)

    def update_streak(self):
        self._check_achievements('streak_updated', {'streak': self.user.streak.current_streak})
   

        # 'streak_updated',
        # 'task_completed',
        # 'task_failed',
        # 'dream_completed',
        # 'item_bought',
        # 'item_equipped',
        # 'total_purchases'