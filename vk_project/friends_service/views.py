from django.forms import model_to_dict
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import User, FriendRequest, FriendShip
from .serializers import (FriendRequestSerializer, 
                          FriendshipSerializer, UserGetSerializer, 
                          UserPostSerializer)

def api_key_check(func):
    '''Декоратор для проверки api_key на действительность,
       После проверки экземляр user передается в функцию
       чтобы дважды не обращаться к одним и тем же данным
    '''
    def wrapper(self, request, *args, **kwargs):
        print(request)
        if (api_key:=kwargs.get('api_key')):
            try:
                if (user:=User.objects.filter(api_key = api_key).first()):
                    return func(self, request, user=user, *args, **kwargs)
                else: 
                    return Response({'Error':'Неверный api_key'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                print('------------------------------------------')
                return Response({'Error':'Ошибка при обработке'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    return wrapper



class UserGetView(generics.ListAPIView):
    '''Возвращает всех пользователей'''
    queryset = User.objects.all()
    serializer_class = UserGetSerializer

class UserPostView(generics.CreateAPIView):
    '''Регистрация нового пользователя'''
    queryset = User.objects.all()
    serializer_class = UserPostSerializer

class UserDelView(views.APIView):
    '''Удаление своего аккаунта'''
    @swagger_auto_schema(responses={
                                    400: 'Неверный api_key',
                                    500: 'Ошибка при обработке'})
    @api_key_check
    def delete(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        user.delete()
        return Response({'Info':'Аккаунт успешно удален'})

# Получение списка исходящих и входящих запросов через токен и отправка заявки
class FriendRequestView(generics.ListCreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    '''Возвращает список входящих и исходящих заявок
    и также обрабатывает отравку заявки в друзья'''
    @swagger_auto_schema(responses={200: 'Запрос успешно выполнен',
                                    400: 'Неверный api_key',
                                    500: 'Ошибка при обработке'})
    @api_key_check
    def get(self, request, user:User = None, *args, **kwargs):
        try:
            api_key = kwargs.get('api_key')
            result = {'outgoing':[], 'incoming':[]}
            for data in [FriendRequest.objects.filter(from_user = user).all(),
                         FriendRequest.objects.filter(to_user = user).all()]:
                for d in data:
                    if d.from_user == user:
                        result['outgoing'].append(model_to_dict(d))
                    elif d.to_user == user:
                        result['incoming'].append(model_to_dict(d))
            return Response(result)
        except:
            return Response({'Error':'Ошибка при обработке'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    @swagger_auto_schema(responses={200: FriendRequestSerializer,
                                    201: FriendshipSerializer,
                                    400: '''Вы пытаетесь отправить заявку самому себе
                                          Вы уже являетесь друзьями
                                          Заявка в друзья уже отправлена
                                          Пользователя с таким id не существует''',
                                    500: 'Ошибка при обработке'})    
    @api_key_check
    def post(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        to_user = request.data.get('to_user')
        if (to_user:=User.objects.filter(id=to_user).first()):
            if user == to_user:
                return Response({'Error': 'Вы пытаетесь отправить заявку самому себе'}, status=status.HTTP_400_BAD_REQUEST)
            elif FriendShip.objects.filter(from_user=user) & FriendShip.objects.filter(to_user = to_user) or\
                 FriendShip.objects.filter(from_user=to_user) & FriendShip.objects.filter(to_user = user):
                return Response({'Info': 'Вы уже являетесь друзьями'}, status=status.HTTP_400_BAD_REQUEST)
            elif FriendRequest.objects.filter(from_user=user) & \
                FriendRequest.objects.filter(to_user = to_user):
                return Response({'Error':'Заявка в друзья уже отправлена'}, status=status.HTTP_400_BAD_REQUEST)
            elif (_:=(FriendRequest.objects.filter(to_user=user) & \
                FriendRequest.objects.filter(from_user = to_user))):
                _.delete()
                friend = FriendShip.objects.create(from_user = user, to_user = to_user)
                return Response({'Info':'У вас новый друг',
                                 'friend':{'id':friend.id, 
                                           'friend_id':friend.to_user.id,
                                           'friend_name':friend.to_user.username}}, status=status.HTTP_201_CREATED)
            else:
                req = FriendRequest.objects.create(from_user = user, to_user = to_user)
                return Response(model_to_dict(req), status=status.HTTP_200_OK)
                
        else: return Response({'Error':'Пользователя с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestDelView(generics.DestroyAPIView):
    '''Удаление отправленной пользователем заявки'''
    @swagger_auto_schema(responses={
                                    400: '''Неверный api_key
                                          У вас нет запроса с таким id
                                          Запроса с таким id не существует''',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check
    def delete(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        if (request_id:=FriendRequest.objects.filter(id=kwargs.get('id')).first()):
            if (request_del:=((FriendRequest.objects.filter(from_user=user) & \
                FriendRequest.objects.filter(id = request_id.id)))):
                request_del.delete()
                return Response({'Info': 'Запрос успешно удален'})
            return Response({'Error':'У вас нет запроса с таким id'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Error':'Запроса с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)

        


class FriendShipView(generics.ListAPIView):
    '''Просмотр всех друзей'''
    @swagger_auto_schema(responses={200:FriendshipSerializer,
                                    400: 'Неверный api_key',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check
    def get(self, request, user:User = None, *args, **kwargs):
        try:
            api_key = kwargs.get('api_key')
            result = {'friends':[]}
            for data in [FriendShip.objects.filter(from_user = user).all(),
                         FriendShip.objects.filter(to_user = user).all()]:
                for d in data:
                    friend = friend if (friend:=d.to_user) != user else d.from_user
                    result['friends'].append({'id':d.id, 
                                              'friend_id':friend.id,
                                              'friend_name':friend.username,})
            return Response(result)
        except:
            return Response({'Error':'Ошибка при обработке'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FriendDelView(generics.DestroyAPIView):
    '''Удаление пользователя из друзей'''
    @swagger_auto_schema(responses={
                                    400: '''Неверный api_key
                                          Пользователь не находится у вас в друзьях
                                          Пользователя с таким id не существует''',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check    
    def delete(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        friend_id = kwargs.get('friend_id')
        if (friend_id:=User.objects.filter(id=friend_id).first()):
            if user == friend_id:
                return Response({'Error': 'Вы пытаетесь удалить самого себя из своих друзей'}, status=status.HTTP_400_BAD_REQUEST)
            elif (friend_del:=(FriendShip.objects.filter(from_user=user) & \
                FriendShip.objects.filter(to_user = friend_id))):
                friend_del.delete()
                return Response({'Info':'Пользователь успешно удален из ваших друзей'})
            elif (friend_del:=(FriendShip.objects.filter(from_user=friend_id) & \
                FriendShip.objects.filter(to_user = user))):
                friend_del.delete()
                return Response({'Info':'Пользователь успешно удален из ваших друзей'})
            else:
                return Response({'Error': 'Пользователь не находится у вас в друзьях'}, status=status.HTTP_400_BAD_REQUEST)
        else: return Response({'Error':'Пользователя с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)



class FriendStatusView(generics.ListAPIView):
    '''Получение статуса с конкретным пользователем'''
    @swagger_auto_schema(responses={200: '''Вы являетесь друзьями
                                          Исходящая заявка
                                          Входящая заявка
                                          Нет ничего''',
                                    400: '''Неверный api_key
                                          Вы указали свой id
                                          Пользователя с таким id не существует''',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check
    def get(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        friend = kwargs.get('friend_id')
        if (friend:=User.objects.filter(id=friend).first()):
            if user == friend:
                return Response({'Error': 'Вы указали свой id'}, status=status.HTTP_400_BAD_REQUEST)
            elif (FriendShip.objects.filter(from_user=user) & FriendShip.objects.filter(to_user = friend)) or\
                (FriendShip.objects.filter(from_user=friend) & FriendShip.objects.filter(to_user = user)):
                return Response({'Info':'Вы являетесь друзьями'})
            elif FriendRequest.objects.filter(from_user=user) & FriendRequest.objects.filter(to_user = friend):
                return Response({'Info':'Исходящая заявка'})
            elif FriendRequest.objects.filter(from_user=friend) & FriendRequest.objects.filter(to_user = user):
                return Response({'Info':'Входящая заявка'})
            else:
                return Response({'Info':'Нет ничего'})
                
        else: return Response({'Error':'Пользователя с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)


class FriendAcceptRequestView(generics.ListAPIView):
    '''Принятие заявки в друзья'''
    @swagger_auto_schema(responses={201: FriendshipSerializer,
                                    400: '''Входящей заявки нет
                                          Неверный api_key
                                          Пользователя с таким id не существует
                                          Вы указали свой id вместо id другого пользователя''',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check
    def get(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        friend = kwargs.get('friend_id')
        if (friend:=User.objects.filter(id=friend).first()):
            if user == friend:
                return Response({'Error': 'Вы указали свой id вместо id другого пользователя'}, status=status.HTTP_400_BAD_REQUEST)
            elif (_:=(FriendRequest.objects.filter(from_user=friend) & FriendRequest.objects.filter(to_user = user))):
                _.delete()
                new_friend = FriendShip.objects.create(from_user = user, to_user=friend)
                return Response({'Info':'Заявка принята', 
                                 'friend':{
                                     'id': new_friend.id,
                                     'friend_id': new_friend.to_user.id,
                                     'friend_name': new_friend.to_user.username}}, status=status.HTTP_201_CREATED)
            else:
                return Response({'Error':'Входящей заявки нет'}, status=status.HTTP_400_BAD_REQUEST)
                
        else: return Response({'Error':'Пользователя с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)




class FriendRejectRequestView(generics.ListAPIView):
    '''Отклонение заявки друзья'''
    @swagger_auto_schema(responses={200: 'Заявка успешно откланена',
                                    400: '''Входящей заявки нет
                                          Неверный api_key
                                          Пользователя с таким id не существует
                                          Вы указали свой id вместо id другого пользователя''',
                                    500: 'Ошибка при обработке'}) 
    @api_key_check
    def get(self, request, user:User = None, *args, **kwargs):
        api_key = kwargs.get('api_key')
        friend = kwargs.get('friend_id')
        if (friend:=User.objects.filter(id=friend).first()):
            if user == friend:
                return Response({'Error': 'Вы указали свой id вместо id другого пользователя'}, status=status.HTTP_400_BAD_REQUEST)
            elif (_:=(FriendRequest.objects.filter(from_user=friend) & FriendRequest.objects.filter(to_user = user))):
                _.delete()
                return Response({'Info':'Заявка отклонена'})
            else:
                return Response({'Error':'Входящей заявки нет'}, status=status.HTTP_400_BAD_REQUEST)
                
        else: return Response({'Error':'Пользователя с таким id не существует'}, status=status.HTTP_400_BAD_REQUEST)
