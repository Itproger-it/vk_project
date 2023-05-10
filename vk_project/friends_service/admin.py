from django.contrib import admin

from .models import User, FriendRequest, FriendShip

admin.site.register(User)
admin.site.register(FriendShip)
admin.site.register(FriendRequest)