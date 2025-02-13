from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import connection

from .models import Room, DB_Message
from .serializers import RoomSerializer, DBMessageSerializer, UserSerializer


# Представление для списка чатов
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_list(request):
    try:
        chats = Room.objects.filter(users=request.user)
        serializer = RoomSerializer(chats, many=True)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": "Чаты не найдены."}, status=status.HTTP_404_NOT_FOUND)


# Представление для создания чата
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat(request):
    if request.method == 'POST':
        data = request.data
        chat_name = data.get('name')

        if not chat_name:
            return Response({'error': 'Имя чата обязательно.'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем чат
        chat = Room.objects.create(name=chat_name)

        # Добавляем текущего пользователя в чат
        user = request.user
        chat.users.add(user)

        serializer = RoomSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Представление для добавления пользователя в чат
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user(request):
    if request.method == 'POST':
        print(request.data)
        data = request.data
        chat_id = data.get('chat_id')
        username = data.get('username')
        if not chat_id or not username:
            return Response({'error': 'Имя чата и имя пользователя обязательны.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Получаем объект комнаты и пользователя
            room = Room.objects.get(id=chat_id)
            user = User.objects.get(username=username)

            # Добавляем пользователя в комнату
            room.users.add(user)
            return Response({'username': username}, status=status.HTTP_201_CREATED)
        except Room.DoesNotExist:
            return Response({'error': 'Комната не найдена.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat(request, room_id):
    user_id = request.user.id
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM "ChatApp_room_users"  WHERE room_id = %s AND user_id = %s', [room_id, user_id])
        return Response({'status': 'Done'}, status=status.HTTP_202_ACCEPTED)
