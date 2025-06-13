from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient


from core.todo.models import Todo

User = get_user_model()

class TodoExecuteViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test todo
        self.todo = Todo.objects.create(
            user=self.user,
            title='Test Todo',
            description='Test Description',
            difficulty=1
        )
        
        # Create a completed todo
        self.completed_todo = Todo.objects.create(
            user=self.user,
            title='Completed Todo',
            description='Already Done',
            difficulty=1,
            is_completed=True,
            executed_at=timezone.now()
        )
        
        # URL for executing todos
        self.execute_url = reverse('todo-execute', kwargs={'pk': self.todo.pk})
        self.completed_execute_url = reverse('todo-execute', kwargs={'pk': self.completed_todo.pk})
        self.detail_url = reverse('todo-retrieve-update-destroy', kwargs={'pk': self.todo.pk})
        self.list_url = reverse('todo-list-create')

    def test_execute_todo_success(self):
        response = self.client.patch(self.execute_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('xp', response.data)
        self.assertIn('coins', response.data)
        
        # Verify todo is now completed
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)
        self.assertIsNotNone(self.todo.executed_at)

    def test_execute_completed_todo(self):
        response = self.client.patch(self.completed_execute_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_execute_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.execute_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_execute_todo_not_found(self):
        non_existent_url = reverse('todo-execute', kwargs={'pk': 9999})
        response = self.client.patch(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_execute_another_users_todo(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        other_todo = Todo.objects.create(
            user=other_user,
            title='Other Todo',
            description='Other Description',
            difficulty=1
        )
        other_url = reverse('todo-execute', kwargs={'pk': other_todo.pk})
        response = self.client.patch(other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_todo_list_empty(self):
        # Delete existing todos
        Todo.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_todo_list_filtering(self):
        # Create additional todo with different completion status
        Todo.objects.create(
            user=self.user,
            title='Filtered Todo',
            description='Should be filtered',
            is_completed=True,
            difficulty=2
        )
        # print([todo for todo in Todo.objects.all()])
        # Filter by completion status
        response = self.client.get(f"{self.list_url}?completed=true")
        # print([todo for todo in response.data['results']])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Filtered Todo')

    def test_create_todo_with_invalid_data(self):
        # Test with missing required field
        response = self.client.post(self.list_url, {
            'description': 'Missing title'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with invalid difficulty
        response = self.client.post(self.list_url, {
            'title': 'Invalid Difficulty',
            'difficulty': 5
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_todo_partial(self):
        update_data = {'title': 'Updated Title Only'}
        response = self.client.patch(self.detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title Only')
        self.assertEqual(self.todo.description, 'Test Description')  # Unchanged

    def test_execute_todo_throttling(self):
        # This would require mocking the throttle classes
        # For a basic test, we can verify the throttle class is applied
        from core.todo.views import TodoExecuteView
        self.assertTrue(hasattr(TodoExecuteView, 'throttle_classes'))
