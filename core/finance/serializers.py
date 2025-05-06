from django.db import transaction as tr
from django.db.models import F, Q

from rest_framework import serializers

from core.finance.models import Deposit, DepositTransaction, FinancialProfile


class FinancialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProfile
        fields = ['id', 'monthly_income', 'monthly_savings']
        read_only_fields = ['id']
    
    #TODO
    def validate(self, attrs):
        return super().validate(attrs)

class DepositTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositTransaction
        fields = ['id', 'deposit', 'amount', 'type', 'created_at']
        read_only_fields = ['id', 'deposit', 'created_at']

    #TODO
    def validate_amont(self, value):
        if value > 100_000_000:
            raise serializers.ValidationError("Слишком большая сумма")
        return value
    
    def update(self, instance: DepositTransaction, validated_data):
        old_amount = instance.amount
        new_amount = validated_data.get('amount', None)

        if new_amount is None: 
            return instance
        
        delta: int = new_amount - old_amount
        with tr.atomic():
            instance.amount = new_amount
            instance.balance_after = new_amount + instance.balance_before
            instance.save(update_fields=['amount', 'balance_after'])

            DepositTransaction.objects.filter(
                Q(deposit=instance.deposit) & Q(id__gt=instance.id)
            ).update(
                balance_before=F('balance_before') + delta,
                balance_after=F('balance_after') + delta
            )

        return instance

class DepositSerializer(serializers.ModelSerializer):
    transactions = DepositTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Deposit
        fields = [
            'id', 'name', 'accrual_type', 'start_amount', 
            'deposit_rate', 'created_at', 'accrual_frequency',
            'term_months', 'replenishable', 'transactions'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    #TODO
    def validate(self, attrs):
        return super().validate(attrs)
