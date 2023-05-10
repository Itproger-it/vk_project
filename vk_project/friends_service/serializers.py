from uuid import uuid4
from rest_framework import serializers
from .models import User, FriendRequest, FriendShip


class UserPostSerializer(serializers.ModelSerializer):
    '''Сериалайзер для добавления юзера'''
    api_key = serializers.UUIDField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'api_key']


class UserGetSerializer(serializers.ModelSerializer):
    '''Сериалайзер для возвращения всех пользователей'''
    class Meta:
        model = User
        fields = ['id', 'username']


class FriendRequestSerializer(serializers.ModelSerializer):
    '''Сериалайзер для отправки заявки'''
    status = serializers.CharField(read_only = True, max_length = 10)
    from_user = serializers.IntegerField(read_only = True)
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created']


class FriendshipSerializer(serializers.ModelSerializer):
    '''Сериалайзер - схема для swagger, представление дру-га(зей)'''
    id = serializers.IntegerField(read_only=True)
    friend_id = serializers.IntegerField(read_only=True)
    friend_name = serializers.IntegerField(read_only=True)
    class Meta:
        model = FriendShip
        fields = ['id', 'friend_id', 'friend_name']
