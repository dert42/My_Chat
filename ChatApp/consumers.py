import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import User

from .models import DB_Message, Room


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']  # Получение аутентифицированного пользователя
        print(f'Authenticated user: {self.user}')  # Проверка аутентификации
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.load_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(text_data)
        await self.save_message(data)

    async def save_message(self, content):
        now = timezone.now()
        room_id = await self.get_room_id()
        if room_id is not None:
            user_instance = self.user  # Используем аутентифицированного пользователя
            message = DB_Message(content=content['message'],
                                 timestamp=now,
                                 user=user_instance,
                                 room_id=room_id)
            await database_sync_to_async(message.save)()
            await self.broadcast(content)

    async def load_messages(self):
        messages = await self.get_messages()
        async for message in messages:
            username = await sync_to_async(lambda: message.user.username)()
            timestamp = str(await sync_to_async(lambda: message.timestamp)())
            await self.send(text_data=json.dumps({
                'message': message.content,
                'user': username,
                'datetime': timestamp,
            }))

    async def broadcast(self, message):
        now = timezone.now()
        username = self.user.username
        await self.channel_layer.group_send(self.room_group_name,
                                             {
                                                 'type': 'chat_message',
                                                 'message': message['message'],
                                                 'user': username,
                                                 'datetime': now.isoformat(),
                                             })

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user': user,
            'datetime': event['datetime'],
        }))

    @database_sync_to_async
    def get_messages(self):
        room_id = Room.objects.filter(name=self.room_name).values_list('id', flat=True).first()
        if room_id is not None:
            return DB_Message.objects.filter(room_id=room_id)
        return []

    @database_sync_to_async
    def get_room_id(self):
        return Room.objects.filter(name=self.room_name).values_list('id', flat=True).first()
