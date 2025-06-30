from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from core.statistic.models import Statistic

User = get_user_model()

@receiver(post_save, sender=User)
def create_statistic_for_user(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'statistic'):
        Statistic.objects.create(user=instance)