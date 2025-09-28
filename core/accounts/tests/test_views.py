from django.test import TestCase
from django.contrib.auth import get_user_model

from core.accounts.models import FriendRelation
from core.authentication.serializers import UserSerializer
User = get_user_model()


class FriendRelationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')

    def test_get_user_friends(self):
        """Get friends list"""
        FriendRelation.objects.create(requester=self.user, recipient=self.other_user, status=FriendRelation.Status.ACCEPTED)
        friends = FriendRelation.get_user_friends(self.user, status=FriendRelation.Status.ACCEPTED  )
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0].username, 'otheruser')

    def test_accept_friend_request(self):
        """Accept friend request"""
        friend_request = FriendRelation.objects.create(requester=self.user, recipient=self.other_user, status=FriendRelation.Status.PENDING)
        friend_request.accept_friend_request()
        self.assertEqual(friend_request.status, FriendRelation.Status.ACCEPTED)

    def test_reject_friend_request(self):
        """Reject friend request"""
        friend_request = FriendRelation.objects.create(requester=self.user, recipient=self.other_user, status=FriendRelation.Status.PENDING)
        friend_request.reject_friend_request()
        self.assertEqual(friend_request.status, FriendRelation.Status.REJECTED)


class FriendRelationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')

    def test_serialize_friend_request(self):
        """Serialize friend request"""
        friend_request = FriendRelation.objects.create(requester=self.user, recipient=self.other_user, status=FriendRelation.Status.PENDING)
        serializer = UserSerializer(friend_request.requester)
        data = serializer.data
        self.assertEqual(data['username'], self.user.username)
