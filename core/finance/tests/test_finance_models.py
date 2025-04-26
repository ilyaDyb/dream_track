from django.test import TestCase
from django.utils import timezone
from decimal import Decimal

from core.authentication.models import User
from core.finance.models import FinancialProfile, Deposit


class FinancialProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.profile = FinancialProfile.objects.create(
            user=self.user,
            monthly_income=Decimal('5000.00')
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.monthly_income, Decimal('5000.00'))
        self.assertIsNotNone(self.profile.updated_at)

    def test_str_representation(self):
        self.assertEqual(str(self.profile), "testuser's Financial Profile")


class DepositModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.profile = FinancialProfile.objects.create(
            user=self.user,
            monthly_income=Decimal('5000.00')
        )
        self.deposit = Deposit.objects.create(
            profile=self.profile,
            amount=Decimal('1000.00'),
            interest_rate=Decimal('5.25'),
            start_date=timezone.now().date(),
            increase_period=30,
            accrual_type=Deposit.AccrualType.RECURRING
        )

    def test_deposit_creation(self):
        self.assertEqual(self.deposit.profile, self.profile)
        self.assertEqual(self.deposit.amount, Decimal('1000.00'))
        self.assertEqual(self.deposit.interest_rate, Decimal('5.25'))
        self.assertEqual(self.deposit.accrual_type, Deposit.AccrualType.RECURRING)
        self.assertTrue(self.deposit.is_active)
        self.assertTrue(self.deposit.is_increasable_all_time)

    def test_str_representation(self):
        self.assertEqual(str(self.deposit), "testuser's Deposit")

    def test_one_time_deposit(self):
        one_time_deposit = Deposit.objects.create(
            profile=self.profile,
            amount=Decimal('2000.00'),
            interest_rate=Decimal('10.00'),
            start_date=timezone.now().date(),
            accrual_type=Deposit.AccrualType.ONE_TIME
        )
        self.assertEqual(one_time_deposit.accrual_type, Deposit.AccrualType.ONE_TIME)
        self.assertEqual(one_time_deposit.amount, Decimal('2000.00'))

    def test_interest_accrual(self):
        self.deposit.accrue_interest()
        self.assertEqual(self.deposit.amount, Decimal('1000.00'))
        self.assertEqual(self.deposit.last_updated.date(), timezone.now().date())

    def test_recurring_deposit(self):
        recurring_deposit = Deposit.objects.create(
            profile=self.profile,
            amount=Decimal('2000.00'),
            interest_rate=Decimal('10.00'),
            start_date=timezone.now().date(),
            accrual_type=Deposit.AccrualType.RECURRING
        )
        self.assertEqual(recurring_deposit.accrual_type, Deposit.AccrualType.RECURRING)
        self.assertEqual(recurring_deposit.amount, Decimal('2000.00'))

    def test_one_time_deposit(self):
        one_time_deposit = Deposit.objects.create(
            profile=self.profile,
            amount=Decimal('2000.00'),
            interest_rate=Decimal('10.00'),
            start_date=timezone.now().date(),
            accrual_type=Deposit.AccrualType.ONE_TIME
        )
        self.assertEqual(one_time_deposit.accrual_type, Deposit.AccrualType.ONE_TIME)
        self.assertEqual(one_time_deposit.amount, Decimal('2000.00'))

    def test_one_time_deposit(self):
        one_time_deposit = Deposit.objects.create(
            profile=self.profile,
            amount=Decimal('2000.00'),
            interest_rate=Decimal('10.00'),
            start_date=timezone.now().date(),
            accrual_type=Deposit.AccrualType.ONE_TIME
        )
        self.assertEqual(one_time_deposit.accrual_type, Deposit.AccrualType.ONE_TIME)
        self.assertEqual(one_time_deposit.amount, Decimal('2000.00'))

