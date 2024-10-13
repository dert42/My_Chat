import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DB_Message


class ChatConsumer(AsyncWebsocketConsumer):
    connected_clients = set()

    async def connect(self):
        # Use the class name to access the class variable
        ChatConsumer.connected_clients.add(self.channel_layer)
        await self.accept()
        await self.load_messages()  # Load messages upon connection

    async def disconnect(self, close_code):
        # Use the class name to access the class variable
        ChatConsumer.connected_clients.remove(self.channel_layer)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.save_message(data['message'])
        await self.send(text_data=json.dumps({'message': data['message']}))

    async def save_message(self, content):
        message = DB_Message(content=content)
        await database_sync_to_async(message.save)()  # Save the message asynchronously

    async def load_messages(self):
        messages = await self.get_messages()  # Get messages asynchronously
        for message in messages:
            await self.send(text_data=json.dumps({'message': message.content}))

    @classmethod
    async def broadcast(cls, message):
        for client in cls.connected_clients:
            await cls.send(client, {'message': message})

    @database_sync_to_async
    def get_messages(self):
        return list(DB_Message.objects.all())  # Retrieve all messages from the database and convert to a list
