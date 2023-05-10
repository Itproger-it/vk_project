from uuid import uuid4
from django.db import models
# from django.contrib.auth.models import AbstractUser


class User(models.Model):
    username = models.CharField(max_length=30)
    api_key = models.UUIDField(default=uuid4)
    
    def __str__(self) -> str:
        return f'{self.username}, id-{self.id}'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='PENDING')
    created = models.DateTimeField(auto_now_add=True)


class FriendShip(models.Model):
    from_user = models.ForeignKey(User, related_name='outgoing_friendships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='incoming_friendships', on_delete=models.CASCADE)