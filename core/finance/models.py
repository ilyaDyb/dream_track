from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class FinancialProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='finance')
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    # savings_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10)  # % откладываемых денег от заработной платы
    monthly_savings = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)],
        help_text="Сумма откладываемых денег за каждый период начисления процентов если позволяет депозит"
    )

    def __str__(self):
        return f"Profile {self.user}"

    class Meta:
        verbose_name = 'Финансовый профиль'
        verbose_name_plural = 'Финансовые профили'
        
class Deposit(models.Model):
    class AccrualType(models.TextChoices):
        RECURRING = 'RC', _('Рекуррентное пополнение (низкий % каждый период)')
        ONE_TIME  = 'OT', _('Одноразовое пополнение (высокий % первый период)')

    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    accrual_type = models.CharField(max_length=2, choices=AccrualType.choices, default=AccrualType.RECURRING)
    #target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    deposit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  # % годовых
    created_at = models.DateTimeField(auto_now_add=True)

    accrual_frequency = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=30,
        help_text="Если указано — частота начисления процентов (в днях)"
    )
    
    term_months   = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True,
        help_text="Если указано — число месяцев до окончания вклада"
    )
    replenishable = models.BooleanField(
        default=True,
        help_text="Можно ли пополнять каждый месяц (True) или нет (False)"
    )

    def __str__(self):
        return f"{self.name} for {self.user}"

    def accrue_interest(self):
        # TODO: Реализовать начисление процентов
        # первые мысли: заупстим крон задачу, которая будет проверять депозиты и начислять проценты
        # если accrual_frequency + self.transactions.filter(type=TransactionType.INTEREST).last().date < timezone.now()
        # то начисляем проценты
        # и добавляем транзакцию
        pass

    def get_amount(self):
        transactions_sum = self.transactions.aggregate(total=Sum('amount'))['total']
        if transactions_sum:
            return self.start_amount + transactions_sum
        return self.start_amount

    def get_history(self):
        return self.transactions.all()

    class Meta:
        verbose_name = 'Вклад'
        verbose_name_plural = 'Вклады'


class DepositTransaction(models.Model):
    class TransactionType(models.TextChoices):
        CONTRIBUTION = 'CONTRIBUTION', _('Пополнение')
        INTEREST     = 'INTEREST', _('Начисление процентов')
    type = models.CharField(max_length=12, choices=TransactionType.choices)

    deposit = models.ForeignKey(Deposit, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, editable=True, validators=[MinValueValidator(0)])
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, editable=True, validators=[MinValueValidator(0)])
    type = models.CharField(max_length=20, choices=TransactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - Amount: {self.amount}, Date: {self.created_at.date()}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate on creation
            self.balance_before = self.deposit.get_amount()
            self.balance_after = self.balance_before + self.amount
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Транзакция по вкладу'
        verbose_name_plural = 'Транзакции по вкладу'

        ordering = ['-created_at']
