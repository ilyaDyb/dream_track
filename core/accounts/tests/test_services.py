from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from datetime import timedelta

from core.accounts.models import UserStreak, Achievement, UserAchievement, UserInventory
from core.accounts.services import UserStreakService, AchievementService, UserAchievementService
from core.shop.models import BackgroundItem


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

User = get_user_model()

class AchievementIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.profile = self.user.profile

        self.item = BackgroundItem.objects.create(
            name='Test BG',
            rarity='common',
            description='test',
            image='bg.jpg',
            price=0,
            type=BackgroundItem.ItemType.BACKGROUND
        )

        self.achievement = Achievement.objects.create(
            code='test_ach',
            title='Test Achievement',
            description='Test Desc',
            trigger='test_trigger',
            condition_data={'tasks_completed': 3},
            reward_xp=100,
            reward_coins=200,
        )
        self.achievement.reward_items.add(self.item)

    def test_achievement_award_and_claim(self):
        service = AchievementService(self.user)
        service.check_achievements('test_trigger', {'tasks_completed': 3})

        self.assertTrue(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).exists())

        claim_service = UserAchievementService(self.user)
        claim_service.activate_achievement(self.achievement.id)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp, 100)
        self.assertEqual(self.profile.balance, 200)

        inventory = UserInventory.objects.filter(user=self.user, item=self.item).first()
        self.assertIsNotNone(inventory)
        self.assertTrue(UserAchievement.objects.get(user=self.user, achievement=self.achievement).is_claimed)

    def test_duplicate_achievement_not_given(self):
        UserAchievement.objects.create(user=self.user, achievement=self.achievement)

        service = AchievementService(self.user)
        service.check_achievements('test_trigger', {'tasks_completed': 3})

        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 1)

    def test_condition_check_fails(self):
        service = AchievementService(self.user)
        service.check_achievements('test_trigger', {'tasks_completed': 2})

        self.assertFalse(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).exists())
