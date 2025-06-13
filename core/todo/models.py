from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.utils import timezone

from core.todo.utils import get_xp_by_lvl, get_coins_by_lvl

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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def execute_task(self):
        self.is_completed = True
        self.deadline = None
        self.executed_at = timezone.now()

        xp_reward = get_xp_by_lvl(self.difficulty)
        coins_reward = get_coins_by_lvl(self.difficulty)
        with transaction.atomic():        
            profile = self.user.profile
            profile.xp += xp_reward
            profile.balance += coins_reward
            profile.save()
            
            self.save()
        
        return xp_reward, coins_reward