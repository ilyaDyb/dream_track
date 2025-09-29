from django.db.models.signals import post_save
from django.dispatch import receiver
from core.accounts.models import UserProfile, UserStreak, DailyRoulette

@receiver(post_save, sender=UserProfile)
def create_streak_for_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance.user, 'streak'):
        UserStreak.objects.create(user=instance.user)


@receiver(post_save, sender=UserProfile)
def create_daily_roulette(sender, instance, created, **kwargs):
    if created and not hasattr(instance.user, 'daily_roulette'):
        DailyRoulette.objects.create(user=instance.user)