from django.apps import AppConfig


class StatisticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.statistic'

    def ready(self):
        import core.statistic.signals