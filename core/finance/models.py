from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from core.authorization.models import User

class FinancialProfile(models.Model):
    user = models.OneToOneField(User, related_name='financial_profile', on_delete=models.CASCADE)

    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Financial Profile"

    class Meta:
        verbose_name = _('Финансовый профиль')
        verbose_name_plural = _('Финансовые профили')

class Deposit(models.Model):
    class AccrualType(models.TextChoices):
        RECURRING = 'RC', _('Рекуррентное пополнение (низкий % каждый период)')
        ONE_TIME  = 'OT', _('Одноразовое пополнение (высокий % первый период)')

    profile = models.ForeignKey(FinancialProfile, related_name='deposits', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    start_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    increase_period = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    accrual_type = models.CharField(max_length=2, choices=AccrualType.choices, default=AccrualType.RECURRING)
    
    is_increasable_all_time = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    
    def accrue_interest(self):
        if self.accrual_type == self.AccrualType.RECURRING:
            # каждый период — начисляем по low_rate
            pass
        else:
            # одноразово — начисляем по high_rate один раз и выключаем
            pass


    def __str__(self):
        return f"{self.profile.user.username}'s Deposit"

    class Meta:
        verbose_name = _('Депозит')
        verbose_name_plural = _('Депозиты')