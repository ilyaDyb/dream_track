from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from core.dream.models import Dream, DreamImage, DreamLike

User = get_user_model()


class DreamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.dream = Dream.objects.create(
            user=self.user,
            title='Test Dream',
            description='Test Description',
            category=Dream.DreamCategory.CAR,
            price=Decimal('1000.00')
        )
        
    def test_dream_creation(self):
        self.assertEqual(self.dream.title, 'Test Dream')
        self.assertEqual(self.dream.description, 'Test Description')
        self.assertEqual(self.dream.category, Dream.DreamCategory.CAR)
        self.assertEqual(self.dream.price, Decimal('1000.00'))
        self.assertEqual(self.dream.is_private, False)
        self.assertEqual(self.dream.is_active, True)
        
    def test_dream_str_method(self):
        self.assertEqual(str(self.dream), 'Test Dream')
        
    def test_dream_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Dream.objects.create(
                user=self.user,
                title='Test Dream',  # Same title for same user
                description='Another Description',
                price=Decimal('500.00')
            )
            
    def test_negative_price_validation(self):
        with self.assertRaises(ValidationError):
            dream = Dream(
                user=self.user,
                title='Negative Price Dream',
                price=Decimal('-100.00')
            )
            dream.full_clean()
            
    def test_dream_category_choices(self):
        self.assertEqual(len(Dream.DreamCategory.choices), 4)
        categories = [choice[0] for choice in Dream.DreamCategory.choices]
        self.assertIn('CAR', categories)
        self.assertIn('TRAVEL', categories)
        self.assertIn('HOME', categories)
        self.assertIn('OTHER', categories)


class DreamImageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='imageuser', password='password123')
        self.dream = Dream.objects.create(
            user=self.user,
            title='Image Test Dream',
            price=Decimal('500.00')
        )
        
    def test_dream_image_relationship(self):
        image = DreamImage.objects.create(
            dream=self.dream,
            image='test_image.jpg'
        )
        self.assertEqual(image.dream, self.dream)
        self.assertEqual(self.dream.images.count(), 1)
        self.assertEqual(self.dream.images.first(), image)


class DreamLikeTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.dream = Dream.objects.create(
            user=self.user1,
            title='Like Test Dream',
            price=Decimal('300.00')
        )
        
    def test_dream_like_creation(self):
        like = DreamLike.objects.create(user=self.user2, dream=self.dream)
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.dream, self.dream)
        self.assertEqual(self.dream.likes.count(), 1)
        
    def test_dream_like_str_method(self):
        like = DreamLike.objects.create(user=self.user2, dream=self.dream)
        expected_str = f"{self.user2.username} liked {self.dream.title}"
        self.assertEqual(str(like), expected_str)
        
    def test_dream_like_unique_constraint(self):
        DreamLike.objects.create(user=self.user2, dream=self.dream)
        with self.assertRaises(IntegrityError):
            DreamLike.objects.create(user=self.user2, dream=self.dream)  # Duplicate like


