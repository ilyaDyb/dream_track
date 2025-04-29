from django.test import TestCase
from decimal import Decimal

from core.authentication.models import User
from core.finance.models import FinancialProfile, Deposit, DepositTransaction

class FinancialProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = FinancialProfile.objects.create(
            user=self.user,
            monthly_income=Decimal('5000.00'),
            monthly_savings=Decimal('500.00')
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.monthly_income, Decimal('5000.00'))
        self.assertEqual(self.profile.monthly_savings, Decimal('500.00'))
        self.assertEqual(str(self.profile), f"Profile {self.user}")

    def test_profile_user_unique_constraint(self):
        with self.assertRaises(Exception):
            FinancialProfile.objects.create(
                user=self.user,
                monthly_income=Decimal('3000.00')
            )


class DepositTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.deposit = Deposit.objects.create(
            name='Test Deposit',
            user=self.user,
            accrual_type=Deposit.AccrualType.RECURRING,
            start_amount=Decimal('1000.00'),
            deposit_rate=Decimal('5.50'),
            term_months=12,
            replenishable=True
        )
        self.transaction = DepositTransaction.objects.create(
            deposit=self.deposit,
            amount=Decimal('200.00'),
            type=DepositTransaction.TransactionType.MANUAL
        )

    def test_deposit_creation(self):
        self.assertEqual(self.deposit.name, 'Test Deposit')
        self.assertEqual(self.deposit.user, self.user)
        self.assertEqual(self.deposit.accrual_type, Deposit.AccrualType.RECURRING)
        self.assertEqual(self.deposit.start_amount, Decimal('1000.00'))
        self.assertEqual(self.deposit.deposit_rate, Decimal('5.50'))
        self.assertEqual(self.deposit.term_months, 12)
        self.assertTrue(self.deposit.replenishable)
        self.assertEqual(str(self.deposit), f"Test Deposit for {self.user}")

    def test_get_amount(self):
        self.assertEqual(self.deposit.get_amount(), Decimal('1200.00'))
        
        # Add another transaction
        DepositTransaction.objects.create(
            deposit=self.deposit,
            amount=Decimal('300.00'),
            type=DepositTransaction.TransactionType.INTEREST
        )
        
        self.assertEqual(self.deposit.get_amount(), Decimal('1500.00'))

    def test_get_history(self):
        transactions = self.deposit.get_history()
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first(), self.transaction)


class DepositTransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.deposit = Deposit.objects.create(
            name='Test Deposit',
            user=self.user,
            start_amount=Decimal('1000.00')
        )
        self.transaction = DepositTransaction.objects.create(
            deposit=self.deposit,
            amount=Decimal('150.00'),
            type=DepositTransaction.TransactionType.INTEREST
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.deposit, self.deposit)
        self.assertEqual(self.transaction.amount, Decimal('150.00'))
        self.assertEqual(self.transaction.type, DepositTransaction.TransactionType.INTEREST)
        self.assertIsNotNone(self.transaction.created_at)
        
        expected_str = f"Начисление процентов 150.00 on {self.transaction.created_at.date()}"
        self.assertEqual(str(self.transaction), expected_str)

    def test_transaction_ordering(self):
        # Create a second transaction
        second_transaction = DepositTransaction.objects.create(
            deposit=self.deposit,
            amount=Decimal('200.00'),
            type=DepositTransaction.TransactionType.MANUAL
        )
        
        # Get ordered transactions
        transactions = self.deposit.transactions.all()
        
        # Check that most recent transaction comes first
        self.assertEqual(transactions.first(), second_transaction)
        self.assertEqual(transactions.last(), self.transaction)
