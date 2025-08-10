from django.db import models


class Statistic(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE, related_name='statistic')

    tasks_completed = models.IntegerField(default=0)
    habits_completed = models.IntegerField(default=0)
    
    items_bought = models.IntegerField(default=0)
    items_equipped = models.IntegerField(default=0)

    dream_completed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Statistic for {self.user}"

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистики'

