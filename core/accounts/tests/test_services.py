from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.accounts.models import UserStreak
from core.accounts.services import UserStreakService


class UserStreakServiceTests(TestCase):
    def setUp(self):
        self.user = MagicMock()
        self.profile = MagicMock()
        self.user.profile = self.profile

        self.streak = MagicMock(spec=UserStreak)
        self.streak.current_streak = 0
        self.streak.max_streak = 0
        self.streak.last_active = timezone.now()
        self.profile.xp = 0
        self.profile.balance = 0

        self.user.streak = self.streak

    def test_get_or_create_streak(self):
        with patch('core.accounts.models.UserStreak.objects.get_or_create') as mock_get_or_create:
            mock_streak = MagicMock()
            mock_get_or_create.return_value = (mock_streak, True)
            
            service = UserStreakService(self.user)
            result = service.get_or_create_streak()
            
            mock_get_or_create.assert_called_once_with(user=self.user)
            self.assertEqual(result, mock_streak)

    def test_create_streak(self):
        with patch('core.accounts.models.UserStreak.objects.create') as mock_create:
            mock_streak = MagicMock()
            mock_create.return_value = mock_streak
            
            service = UserStreakService(self.user)
            service.create_streak()
            
            mock_create.assert_called_once_with(
                user=self.user,
                current_streak=0,
                max_streak=0,
            )
            self.assertEqual(service.streak, mock_streak)

    def test_increase_streak_with_recent_activity(self):
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        self.streak.last_active = yesterday
        self.streak.current_streak = 5
        self.streak.max_streak = 10
        
        service = UserStreakService(self.user)
        service.increase_streak()
        
        self.assertEqual(self.streak.current_streak, 6)
        self.streak.save.assert_called_with(update_fields=['current_streak', 'max_streak', 'last_active'])

    def test_increase_streak_with_old_activity(self):
        today = timezone.now()
        two_days_ago = today - timedelta(days=2)
        self.streak.last_active = two_days_ago
        self.streak.current_streak = 5
        
        service = UserStreakService(self.user)
        service.increase_streak()
        
        self.assertEqual(self.streak.current_streak, 1)
        self.streak.save.assert_called_with(update_fields=['current_streak', 'max_streak', 'last_active'])

    def test_update_max_streak(self):
        self.streak.current_streak = 10
        self.streak.max_streak = 10
        
        service = UserStreakService(self.user)
        service.update_streak()
        
        self.assertEqual(self.streak.current_streak, 11)
        self.assertEqual(self.streak.max_streak, 11)

    @patch('django.utils.timezone.now')
    def test_reward_milestone(self, mock_now):
        service = UserStreakService(self.user)
        
        # Test 7-day milestone
        self.streak.current_streak = 7
        service._reward_milestone()
        self.profile.save.assert_called_with(update_fields=['xp', 'balance'])
        self.assertEqual(self.profile.xp, 100)
        self.assertEqual(self.profile.balance, 100)

        # Reset and test 30-day milestone
        self.profile.xp = 0
        self.profile.balance = 0
        self.streak.current_streak = 30
        service._reward_milestone()
        self.assertEqual(self.profile.xp, 200)
        self.assertEqual(self.profile.balance, 200)
