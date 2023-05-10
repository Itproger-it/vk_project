from django.forms import model_to_dict
from rest_framework.test import APITestCase

from friends_service.models import User, FriendRequest, FriendShip


class ModelsTestCase(APITestCase):

    def test_user_model(self):
        user1 = User.objects.create(username = 'test1')
        user1 = model_to_dict(user1)
        data1 = {'id':1, 'username':'test1'}
        self.assertEqual(user1, user1|data1)

        user2 = User.objects.create(username = 'test2')
        user2 = model_to_dict(user2)
        data2 = {'id':2, 'username':'test2'}
        self.assertEqual(user2, user2|data2)

    def test_friend_request_model(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        fr1 = FriendRequest.objects.create(from_user = user1, to_user=user2)
        fr1 = model_to_dict(fr1)
        data = {'id':1, 'from_user': user1.id, 'to_user':user2.id, 'status': 'PENDING'}
        self.assertEqual(data, fr1|data)


    def test_friend_ship(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        f1 = FriendShip.objects.create(from_user = user1, to_user=user2)
        f1 = model_to_dict(f1)
        data = {'id':1, 'from_user': user1.id, 'to_user':user2.id}
        self.assertEqual(data, data|f1)
