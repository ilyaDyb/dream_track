from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.utils import timezone

from core.accounts.progress import UserActionProgressService
from core.todo.utils import get_xp_by_lvl, get_coins_by_lvl
from core.accounts.services import UserStreakService

User = get_user_model()

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    difficulty = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    is_dream_step = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def execute_task(self):
        self.deadline = None
        self.is_completed = True
        self.executed_at = timezone.now()

        todo_service = TodoService(self)

        with transaction.atomic():
            xp, coins = todo_service.apply_rewards()
            self.save()
            UserActionProgressService(self.user).update_stat('task_completed')
        
        return xp, coins

class TodoService:
    def __init__(self, task: Todo) -> None:
        self.task = task
        self.user = task.user
        self.profile = self.user.profile
        self.boosts = {b.boost.boost_type: b.boost.multiplier for b in self.user.boosts.all() if b.expires_at > timezone.now()}

    
    def get_multiplier(self, boost_type: str) -> float:
        return self.boosts.get(boost_type, 1.0)

    def calculate_rewards(self):
        xp = get_xp_by_lvl(self.task.difficulty)
        coins = get_coins_by_lvl(self.task.difficulty)
        xp *= self.get_multiplier('xp')
        coins *= self.get_multiplier('coins')
        return int(xp), int(coins)
    
    def apply_rewards(self) -> tuple[int, int]:
        # Streak earn
        self._increase_streak()

        # Profile earn
        xp, coins = self.calculate_rewards()
        self.profile.xp += xp
        self.profile.balance += coins
        self.profile.save()
        return xp, coins

        
    def _increase_streak(self) -> None:
        UserStreakService(self.user).increase_streak()
        