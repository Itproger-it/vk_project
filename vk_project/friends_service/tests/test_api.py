from django.forms import model_to_dict
from django.urls import reverse
from rest_framework.test import APITestCase

from friends_service.models import User, FriendRequest, FriendShip

class UserApiTestCase(APITestCase):

    def test_get_users(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        data = [
            {
                'id': user1.id,
                'username':user1.username
            }, 
            {
                'id': user2.id,
                'username' :user2.username
            }]
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(data, list(response.data))

    def test_create_user(self):
        data = {
            'id': 1,
            'username': 'test1'
        }
        url = reverse('add-user')
        response = self.client.post(url, data={"username":"test1"}, format='json')
        response = dict(response.data)
        del response['api_key']
        self.assertEqual(data, response)

    def test_delete_user(self):
        user1 = User.objects.create(username = 'test1')
        url = f'/api/v1/user-delete/{str(user1.api_key)}'
        
        response = self.client.delete(url)
        self.assertEqual('Аккаунт успешно удален', response.data['Info'])


class FriendRequestApiTestCase(APITestCase):

    def test_get_request(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')

        req1 = FriendRequest.objects.create(from_user = user1, to_user = user2)
        req2 = FriendRequest.objects.create(from_user = user1, to_user = user3)
        data = {'outgoing': [model_to_dict(req1), model_to_dict(req2)], 'incoming':[]}

        url = f'/api/v1/friend-request/{str(user1.api_key)}'
        response = self.client.get(url)
        self.assertEqual(data, dict(response.data))


    def test_post_request(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')

        data = {
            'id': 1,
            'from_user':user1.id,
            'to_user': user2.id,
            'status': 'PENDING',

        }

        url = f'/api/v1/friend-request/{str(user1.api_key)}'
        
        response = self.client.post(url, data={"to_user": user1.id}, format='json')
        self.assertEqual('Вы пытаетесь отправить заявку самому себе', response.data['Error'])

        response = self.client.post(url, data={"to_user": user2.id}, format='json')
        self.assertEqual(data, dict(response.data))

        response = self.client.post(url, data={"to_user": user2.id}, format='json')
        self.assertEqual('Заявка в друзья уже отправлена', response.data['Error'])

        response = self.client.post(url, data={"to_user": 10}, format='json')
        self.assertEqual('Пользователя с таким id не существует', response.data['Error'])


    def test_delete_request(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')

        req1 = FriendRequest.objects.create(from_user=user1, to_user=user2)
        req2 = FriendRequest.objects.create(from_user=user2, to_user=user3)
        
        url = f'/api/v1/friend-request/{str(user1.api_key)}/{req1.id}/delete'
        response = self.client.delete(url)
        self.assertEqual('Запрос успешно удален', response.data['Info'])

        url = f'/api/v1/friend-request/{str(user1.api_key)}/{req2.id}/delete'
        response = self.client.delete(url)
        self.assertEqual('У вас нет запроса с таким id', response.data['Error'])

        url = f'/api/v1/friend-request/{str(user1.api_key)}/{5}/delete'
        response = self.client.delete(url)
        self.assertEqual('Запроса с таким id не существует', response.data['Error'])


    def test_accept_request(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')

        req1 = FriendRequest.objects.create(from_user=user1, to_user=user2)
        req2 = FriendRequest.objects.create(from_user=user2, to_user=user3)
        
        url = f'/api/v1/friends-request/{str(user1.api_key)}/{user1.id}/accept'
        response = self.client.get(url)
        self.assertEqual('Вы указали свой id вместо id другого пользователя', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user1.api_key)}/{user3.id}/accept'
        response = self.client.get(url)
        self.assertEqual('Входящей заявки нет', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user1.api_key)}/{5}/accept'
        response = self.client.get(url)
        self.assertEqual('Пользователя с таким id не существует', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user2.api_key)}/{user1.id}/accept'
        data = {
            'Info':'Заявка принята',
            'friend': {
                'id': 1,
                'friend_id': 1,
                'friend_name': 'test1'
            }
        }
        response = self.client.get(url)
        self.assertEqual(data, dict(response.data))


    def test_reject_request(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')

        req1 = FriendRequest.objects.create(from_user=user1, to_user=user2)
        req2 = FriendRequest.objects.create(from_user=user2, to_user=user3)
        
        url = f'/api/v1/friends-request/{str(user1.api_key)}/{user1.id}/reject'
        response = self.client.get(url)
        self.assertEqual('Вы указали свой id вместо id другого пользователя', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user1.api_key)}/{user3.id}/reject'
        response = self.client.get(url)
        self.assertEqual('Входящей заявки нет', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user1.api_key)}/{5}/reject'
        response = self.client.get(url)
        self.assertEqual('Пользователя с таким id не существует', response.data['Error'])

        url = f'/api/v1/friends-request/{str(user2.api_key)}/{user1.id}/reject'
        response = self.client.get(url)
        self.assertEqual('Заявка отклонена', response.data['Info'])


class FriendShipTestCase(APITestCase):

    def test_get_friends(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')
        user4 = User.objects.create(username = 'test4')

        f1 = FriendShip.objects.create(from_user=user1, to_user=user2)
        f2 = FriendShip.objects.create(from_user=user1, to_user=user3)

        url = f'/api/v1/friends/{str(user4.api_key)}'
        data = {
            'friends':[]
        }
        response = self.client.get(url)
        self.assertEqual(data, dict(response.data))

        url = f'/api/v1/friends/{str(user1.api_key)}'
        data = {
            'friends':[
                {
                    'id': f1.id,
                    'friend_id': f1.to_user.id,
                    'friend_name': f1.to_user.username
                },
                {
                    'id': f2.id,
                    'friend_id': f2.to_user.id,
                    'friend_name': f2.to_user.username
                }
            ]
        }
        response = self.client.get(url)
        self.assertEqual(data, dict(response.data))

        url = f'/api/v1/friends/{str(user3.api_key)}'
        data = {
            'friends':[
                {
                    'id': f2.id,
                    'friend_id': f1.from_user.id,
                    'friend_name': f1.from_user.username
                }
            ]
        }
        response = self.client.get(url)
        self.assertEqual(data, dict(response.data))


    def test_delete_friends(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')
        user4 = User.objects.create(username = 'test4')

        f1 = FriendShip.objects.create(from_user=user1, to_user=user2)
        f2 = FriendShip.objects.create(from_user=user1, to_user=user3)
        f3 = FriendShip.objects.create(from_user=user2, to_user=user3)

        url = f'/api/v1/friend-delete/{str(user1.api_key)}/{user1.id}'
        response = self.client.delete(url)
        self.assertEqual('Вы пытаетесь удалить самого себя из своих друзей', response.data['Error'])

        url = f'/api/v1/friend-delete/{str(user1.api_key)}/{user2.id}'
        response = self.client.delete(url)
        self.assertEqual('Пользователь успешно удален из ваших друзей', response.data['Info'])

        url = f'/api/v1/friend-delete/{str(user3.api_key)}/{user1.id}'
        response = self.client.delete(url)
        self.assertEqual('Пользователь успешно удален из ваших друзей', response.data['Info'])

        url = f'/api/v1/friend-delete/{str(user1.api_key)}/{user4.id}'
        response = self.client.delete(url)
        self.assertEqual('Пользователь не находится у вас в друзьях', response.data['Error'])

        url = f'/api/v1/friend-delete/{str(user2.api_key)}/{10}'
        response = self.client.delete(url)
        self.assertEqual('Пользователя с таким id не существует', response.data['Error'])


    def test_status_users(self):
        user1 = User.objects.create(username = 'test1')
        user2 = User.objects.create(username = 'test2')
        user3 = User.objects.create(username = 'test3')
        user4 = User.objects.create(username = 'test4')

        req1 = FriendRequest.objects.create(from_user=user3, to_user = user4)

        f1 = FriendShip.objects.create(from_user=user1, to_user=user2)
        f2 = FriendShip.objects.create(from_user=user1, to_user=user3)

        url = f'/api/v1/friends-status/{str(user1.api_key)}/{user1.id}'
        response = self.client.get(url)
        self.assertEqual('Вы указали свой id', response.data['Error'])

        url = f'/api/v1/friends-status/{str(user1.api_key)}/{user2.id}'
        response = self.client.get(url)
        self.assertEqual('Вы являетесь друзьями', response.data['Info'])

        url = f'/api/v1/friends-status/{str(user3.api_key)}/{user4.id}'
        response = self.client.get(url)
        self.assertEqual('Исходящая заявка', response.data['Info'])

        url = f'/api/v1/friends-status/{str(user4.api_key)}/{user3.id}'
        response = self.client.get(url)
        self.assertEqual('Входящая заявка', response.data['Info'])

        url = f'/api/v1/friends-status/{str(user1.api_key)}/{user4.id}'
        response = self.client.get(url)
        self.assertEqual('Нет ничего', response.data['Info'])

        url = f'/api/v1/friends-status/{str(user2.api_key)}/{10}'
        response = self.client.get(url)
        self.assertEqual('Пользователя с таким id не существует', response.data['Error'])