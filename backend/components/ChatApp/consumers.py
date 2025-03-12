import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.http import Http404
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.db import connection
from django.shortcuts import get_object_or_404
from abc import ABC, abstractmethod

from components.accounts.models import ProfilePicture


class ChatRepository:
    @staticmethod
    @database_sync_to_async
    def get_messages(room_id):
        # room_id = Room.objects.filter(name=self.room_name).values_list('id', flat=True).first()
        if room_id is not None:
            # DB_Message.objects.filter(room_id=room_id)
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM "ChatApp_db_message" WHERE room_id = %s ORDER BY id;', [room_id])
                messages = cursor.fetchall()
            return messages

    @staticmethod
    @database_sync_to_async
    def get_username(user_id):
        print(user_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT username FROM "auth_user" WHERE id = %s', [user_id])
            username = cursor.fetchone()
            username = username[0]
            return username

    @staticmethod
    @database_sync_to_async
    def get_avatar(user_id):
        try:
            avatar_url = get_object_or_404(ProfilePicture, user_id=user_id)
            return avatar_url.get_avatar_url()
        except Http404:
            return None

    @staticmethod
    @sync_to_async
    def insert_message(msg_content, timestamp, user_id, msg_room_id):
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO "ChatApp_db_message" (content, timestamp, user_id, room_id, edited)'
                           'VALUES (%s, %s, %s, %s, FALSE)',
                           (msg_content, timestamp, user_id, msg_room_id)
                           )

    @staticmethod
    @sync_to_async
    def update_message(new_msg, msg_id):
        edited = True
        with connection.cursor() as cursor:
            cursor.execute('UPDATE "ChatApp_db_message"'
                           'SET content = %s,'
                           'edited = %s '
                           'WHERE id = %s', [new_msg, edited, msg_id])

    @staticmethod
    @sync_to_async
    def delete_message(msg_id):
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM "ChatApp_db_message"'
                           'WHERE id = %s', [msg_id])


class Command(ABC):
    """Базовый интерфейс для всех команд."""

    @abstractmethod
    async def execute(self, data: dict):
        pass


class SaveMessageCommand(Command):
    def __init__(self, consumer: 'ChatConsumer', repository: 'ChatRepository'):
        self.consumer = consumer
        self.data = None
        self.repository = repository

    async def execute(self, data: dict):
        self.data = data
        now = timezone.now()
        if self.consumer.room_id is not None:
            user_instance_id = self.consumer.user.id
            await self.repository.insert_message(self.data['message'], now, user_instance_id, self.consumer.room_id)
            await self.consumer.broadcast(self.data)


class EditCommand(Command):
    def __init__(self, consumer: 'ChatConsumer', repository: 'ChatRepository'):
        self.consumer = consumer
        self.data = None
        self.repository = repository

    async def execute(self, data: dict):
        self.data = data
        await self.repository.update_message(self.data['new_text'], self.data['message_id'])
        await self.consumer.send(text_data=json.dumps({
            'type': 'edit',
            'message_id': self.data['message_id'],
            'new_text': self.data['new_text']
        }))


class DeleteCommand(Command):
    def __init__(self, consumer: 'ChatConsumer', repository: 'ChatRepository'):
        self.consumer = consumer
        self.data = None
        self.repository = repository

    async def execute(self, data: dict):
        self.data = data
        await self.repository.delete_message(self.data['message_id'])
        await self.consumer.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': self.data['message_id'],
        }))


class ChatCommandHandler:
    def __init__(self, consumer: 'ChatConsumer', repository: 'ChatRepository'):
        self.consumer = consumer
        self.repository = repository
        self.commands = {
            "message": SaveMessageCommand(consumer, repository),
            "edit": EditCommand(consumer, repository),
            "delete": DeleteCommand(consumer, repository),
        }

    async def handle(self, data):
        command = data.get("type")
        if command in self.commands:
            await self.commands[command].execute(data)  # Вызываем метод execute()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']  # Получение аутентифицированного пользователя
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_id = f'{self.room_id}'
        self.repository = ChatRepository()
        self.command_handler = ChatCommandHandler(self, self.repository)  # Обработчик команд
        await self.channel_layer.group_add(self.room_group_id, self.channel_name)
        await self.accept()
        await self.load_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.command_handler.handle(data)

    async def load_messages(self):
        messages = await self.repository.get_messages(self.room_id)
        for message in messages:
            message_id = message[0]
            user_id = message[4]
            print(message)
            print(user_id)
            username = await self.repository.get_username(user_id)
            timestamp = str(message[2])
            avatar_url = await self.repository.get_avatar(user_id)
            edited = bool(message[5])
            await self.send(text_data=json.dumps({
                'id': message_id,
                'message': message[1],
                'user': username,
                'datetime': timestamp,
                'avatar_url': avatar_url,
                'edited': edited,
            }))

    async def broadcast(self, message):
        now = timezone.now()
        username = self.user.username
        user_id = self.user.id
        avatar_url = await self.repository.get_avatar(user_id)
        await self.channel_layer.group_send(self.room_group_id,
                                            {
                                                'type': 'chat_message',
                                                'message': message['message'],
                                                'user': username,
                                                'datetime': now.isoformat(),
                                                'avatar_url': avatar_url,
                                                'edited': False,
                                            })

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user': user,
            'datetime': event['datetime'],
            'avatar_url': event['avatar_url'],
            'edited': False,
        }))
