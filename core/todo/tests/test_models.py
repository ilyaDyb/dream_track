from django.test import TestCase
from django.contrib.auth import get_user_model
from core.todo.models import Todo, TodoService
from unittest.mock import patch

User = get_user_model()

class TestRewardServiceIntegration(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        # убедись что профиль создан (если у тебя сигнал создает профиль)

    def test_is_golden_integration(self):
        todo = Todo.objects.create(user=self.user, title='t', is_golden=True, difficulty=1)
        # патчим только базовые функции
        with patch('core.todo.models.get_xp_by_lvl', return_value=10), \
             patch('core.todo.models.get_coins_by_lvl', return_value=5):
            service = TodoService(todo)
            xp, coins = service.apply_rewards()

        self.assertEqual(xp, 20)
        self.assertEqual(coins, 10)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp, 20)
