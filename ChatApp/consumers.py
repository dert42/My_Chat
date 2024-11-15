import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import DB_Message
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        await self.channel_layer.group_add('chat', self.channel_name)
        await self.accept()
        await self.load_messages()  # Загрузка сообщений при подключении

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('chat', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.save_message(data['message'])
        await self.broadcast(data['message'])

    async def save_message(self, content):
        now = timezone.now()
        message = DB_Message(content=content,
                             timestamp=now,
                             user=self.user)
        await database_sync_to_async(message.save)()  # Асинхронное сохранение сообщения

    async def load_messages(self):
        messages = await self.get_messages()  # Get messages directly
        for message in messages:
            username = await sync_to_async(lambda: message.user.username)()
            timestamp = str(await sync_to_async(lambda: message.timestamp)())
            await self.send(text_data=json.dumps({
                'message': message.content,
                'user': username,  # Username
                'datetime': timestamp,  # Message timestamp
            }))

    async def broadcast(self, message):
        now = timezone.now()
        username = self.user.username  # Получаем имя пользователя
        await self.channel_layer.group_send('chat',
            {   'type': 'chat_message',
                'message': message,
                'user': username,
                'datetime': now.isoformat(),
            }
        )

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
        return list(DB_Message.objects.all())  # Извлечение сообщений для конкретной комнаты

