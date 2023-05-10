from rest_framework.test import APITestCase

from friends_service.serializers import UserGetSerializer, UserPostSerializer
from friends_service.models import User

class UserSerializerTestCase(APITestCase):

    def test_get_ok(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')

        data = UserGetSerializer([user1, user2], many = True).data

        expected_data = [
            {
                'id':user1.id,
                'username': user1.username
            },
            {
                'id':user2.id,
                'username': user2.username
            }
        ]
        self.assertEqual(expected_data, data)


    def test_post_ok(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')

        data = UserPostSerializer([user1, user2], many = True).data

        expected_data = [
            {
                'id':user1.id,
                'username': user1.username,
                'api_key': str(user1.api_key)
            },
            {
                'id':user2.id,
                'username': user2.username,
                'api_key': str(user2.api_key)
            }
        ]
        self.assertEqual(expected_data, data)

