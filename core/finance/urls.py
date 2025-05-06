from django.urls import path

from core.finance.views import (
    FinancialProfileListCreateView,
    FinancialProfileDetailView,
    DepositListCreateView,
    DepositDetailView,
    DepositTransactionListCreateView,
    DepositTransactionDetailView
)


app_name = 'finance'

urlpatterns = [
    
    path('financial-profile/<int:id>/', FinancialProfileListCreateView.as_view(), name='financial_profile_detail'),
    path('financial-profile/', FinancialProfileDetailView.as_view(), name='financial_profile_list'),
    path('deposits/', DepositListCreateView.as_view(), name='deposit_list_create'),
    path('deposits/<int:id>/', DepositDetailView.as_view(), name='deposit_detail'),
    path('deposits/<int:id>/transactions/', DepositTransactionListCreateView.as_view(), name='deposit_transactions_list'),
    path('deposits/<int:id>/transactions/<int:transaction_id>/', DepositTransactionDetailView.as_view(), name='deposit_transaction_detail'),
    # financial-profile/<int:id>
    # financial-profile/

    # deposits/
    # deposits/<int:id>
    # deposits/<int:id>/transactions 
    # deposits/<int:id>/transactions/<int:transaction_id>
]
