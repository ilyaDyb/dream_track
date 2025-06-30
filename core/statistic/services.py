
# class StatisticService:
#     def __init__(self, user):
#         self.user = user
#         self.statistic = user.statistic

#     def update(self, key, value=1):
#         """
#         Обновляет поле в модели Statistic
#         """
#         try:
#             nvalue = getattr(self.statistic, key) + value
#             setattr(self.statistic, key, nvalue)
#             with transaction.atomic():
#                 self.statistic.save(update_fields=[key])
#                 self.check_achievements(key)
#         except AttributeError:
#             raise ValueError(f"Invalid field name: {key}")
        

#     def check_achievements(self, key):
#         AchievementService(self.user).check_achievements(key, {key: getattr(self.statistic, key)})