import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DB_Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Добавление клиента в общую группу 'chat'
        await self.channel_layer.group_add(
            'chat',  # Убедитесь, что группа называется 'chat'
            self.channel_name
        )

        await self.accept()
        await self.load_messages()  # Загрузка сообщений при подключении

    async def disconnect(self, close_code):
        # Удаление клиента из группы при отключении
        await self.channel_layer.group_discard(
            'chat',  # Убедитесь, что группа называется 'chat'
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.save_message(data['message'])
        await self.broadcast(data['message'])

    async def save_message(self, content):
        message = DB_Message(content=content)
        await database_sync_to_async(message.save)()  # Асинхронное сохранение сообщения

    async def load_messages(self):
        messages = await self.get_messages()  # Получить сообщения асинхронно
        for message in messages:
            await self.send(text_data=json.dumps({'message': message.content}))

    async def broadcast(self, message):
        # Асинхронная отправка сообщения всем подключенным клиентам
        await self.channel_layer.group_send(
            'chat',  # Используем имя группы 'chat'
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    @database_sync_to_async
    def get_messages(self):
        return list(DB_Message.objects.all())  # Извлечение всех сообщений из базы данных и преобразование в список
