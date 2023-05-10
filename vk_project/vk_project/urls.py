"""
URL configuration for vk_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import permissions
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from friends_service.views import (UserGetView, UserPostView, 
                                   FriendRequestView, FriendShipView,
                                   FriendDelView, FriendStatusView,
                                   FriendAcceptRequestView, FriendRequestDelView,
                                   FriendRejectRequestView, UserDelView)

schema_view = get_schema_view(
   openapi.Info(
      title="Friends Service API",
      default_version='v1',
    #   description="Test description",
    #   terms_of_service="https://www.google.com/policies/terms/",
    #   contact=openapi.Contact(email="contact@snippets.local"),
    #   license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', UserGetView.as_view(), name='users'),
    path('api/v1/add-user/', UserPostView.as_view(), name='add-user'),
    path('api/v1/user-delete/<uuid:api_key>', UserDelView.as_view()),
    path('api/v1/friend-request/<uuid:api_key>', FriendRequestView.as_view()),
    path('api/v1/friend-request/<uuid:api_key>/<int:id>/delete', FriendRequestDelView.as_view()),
    path('api/v1/friends/<uuid:api_key>', FriendShipView.as_view()),
    path('api/v1/friend-delete/<uuid:api_key>/<int:friend_id>', FriendDelView.as_view()),
    path('api/v1/friends-status/<uuid:api_key>/<int:friend_id>', FriendStatusView.as_view()),
    path('api/v1/friends-request/<uuid:api_key>/<int:friend_id>/accept', FriendAcceptRequestView.as_view()),
    path('api/v1/friends-request/<uuid:api_key>/<int:friend_id>/reject', FriendRejectRequestView.as_view()),

    re_path(r'^swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

