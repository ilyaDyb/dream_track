# from django.utils import timezone
# from datetime import timedelta, date
# from decimal import Decimal

# from core.finance.models import FinancialProfile, SavingsGoal

# class DepositService:    
#     @staticmethod
#     def accrue_interest(deposit):
#         if deposit.accrual_type == deposit.AccrualType.RECURRING and deposit.date_when_increase <= timezone.now().date():
#             deposit.amount += deposit.amount * (deposit.interest_rate / 100) + deposit.profile.monthly_income
#             deposit.date_when_increase += timedelta(days=deposit.increase_period)
#         else:
#             deposit.amount += deposit.amount * (deposit.interest_rate / 100)
#             deposit.date_when_increase += timedelta(days=deposit.increase_period)
#         deposit.save()
    
#     @staticmethod
#     def additional_replenishment(amount, deposit):
#         if deposit.accrual_type == deposit.AccrualType.ONE_TIME:
#             raise ValueError("One-time deposit cannot be replenished")
#         else:
#             deposit.amount += amount
#             deposit.save()

    
    # @staticmethod
    # def calculate_savings_projection(profile, goal, dream):
    #     """
    #     profile: FinancialProfile
    #     goal:    SavingsGoal
    #     dream:   объект мечты с атрибутом price
    #     Возвращает dict или сообщение о невозможности накопить
    #     """

    #     monthly_contrib = profile.monthly_savings

    #     balance = goal.start_amount
    #     target  = dream.price
    #     apr     = goal.deposit_rate / Decimal('100')
    #     term    = goal.term_months
    #     month   = 0

    #     total_contrib = Decimal('0')
    #     total_interest= Decimal('0')
    #     history       = []

    #     while month < 600:
    #         month += 1

    #         # 1) начисляем проценты
    #         interest = balance * (apr / Decimal('12'))
    #         balance += interest
    #         total_interest += interest

    #         # 2) добавляем вклад
    #         contribution = Decimal('0')
    #         if goal.replenishable:
    #             balance += monthly_contrib
    #             total_contrib += monthly_contrib
    #             contribution = monthly_contrib
    #         else:
    #             if term and (month % term == 0):
    #                 balance += monthly_contrib
    #                 total_contrib += monthly_contrib
    #                 contribution = monthly_contrib

    #         # 3) сохраняем в историю
    #         history.append({
    #             'month':        month,
    #             'date':         (date.today() + timedelta(days=30*month)).isoformat(),
    #             'contribution': float(round(contribution, 2)),
    #             'interest':     float(round(interest, 2)),
    #             'balance':      float(round(balance, 2)),
    #         })

    #         # 4) проверка достижения цели
    #         if balance >= target:
    #             return {
    #                 'months_needed':      month,
    #                 'total_contributions': float(round(total_contrib, 2)),
    #                 'total_interest':      float(round(total_interest, 2)),
    #                 'final_balance':       float(round(balance, 2)),
    #                 'history':             history,
    #             }

    #     # Если не накопили за 600 месяцев
    #     return {
    #         'error': 'Вы не сможете накопить такую сумму при текущих условиях',
    #         'months_passed': month,
    #         'final_balance': float(round(balance, 2)),
    #         'history':       history,
    #     }

# if __name__ == '__main__':
# from core.finance.services import DepositService
# profile = FinancialProfile.objects.first()
# goal = SavingsGoal.objects.first()
# dream = Dream.objects.first()
# DepositService.calculate_savings_projection(profile, goal, dream)
#     res = DepositService.calculate_savings_projection(profile, goal, dream)
#     print(res)