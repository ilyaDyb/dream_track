from django.contrib import admin
from .models import FinancialProfile, Deposit, DepositTransaction

admin.site.register(FinancialProfile)
admin.site.register(Deposit)
admin.site.register(DepositTransaction)