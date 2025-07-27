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
    dream = models.ForeignKey('dream.Dream', on_delete=models.CASCADE, related_name='steps', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.is_dream_step and self.dream is None:
            raise ValidationError("Dream step must be associated with a dream")
    
        if not self.is_dream_step and self.dream is not None:
            raise ValidationError("Non-dream step should not be associated with a dream")


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
    
    def apply_rewards(self) -> tuple[int, int]:
        # Streak earn
        self._increase_streak()

        # Profile earn
        xp, coins = RewardService(self.task).calculate_rewards()
        self.profile.xp += xp
        self.profile.balance += coins
        self.profile.save()
        return xp, coins
   
    def _increase_streak(self) -> None:
        UserStreakService(self.user).increase_streak()

class RewardService:
    # def __init__(self, obj: Todo | Habit) -> None:
    def __init__(self, obj: Todo) -> None:
        self.obj = obj
        self.user = obj.user
        self.profile = self.user.profile
    
    def calculate_rewards(self):
        xp = get_xp_by_lvl(self.obj.difficulty)
        coins = get_coins_by_lvl(self.obj.difficulty)
        xp *= self.get_multiplier('xp')
        coins *= self.get_multiplier('coins')
        return int(xp), int(coins)
    
    def get_multiplier(self, boost_type: str) -> float:
        boosts = {b.boost.boost_type: b.boost.multiplier for b in self.user.boosts.all() if b.expires_at > timezone.now()}
        return boosts.get(boost_type, 1.0)

# class Habit(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
#     title = models.CharField(max_length=255)
#     description = models.CharField(max_length=2048, blank=True, null=True)
#     difficulty = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])

#     streak = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return self.title

#     def execute_habit(self):
#         self.streak += 1
#         xp, coins = RewardService(self).calculate_rewards()
#         self.user.profile.xp += xp
#         self.user.profile.balance += coins
#         with transaction.atomic():
#             self.user.profile.save()
#             self.save()
    # class Meta:
    #     verbose_name = 'Привычка'
    #     verbose_name_plural = 'Привычки'