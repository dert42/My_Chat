import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoCallConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_id = 'general_group'
        self.call_id = None
        await self.channel_layer.group_add(self.room_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        data_type = data.get('type')
        if data_type == 'call-invite':
            await self.call_invite_handler(data)
        elif data_type == 'create-call':
            self.call_id = str(uuid.uuid4())
            await self.channel_layer.group_add(self.call_id, self.channel_name)
            await self.send(text_data=json.dumps({
              'type': 'call-created',
              'target': data.get('target'),
              'from': data.get('from'),
              'callId': self.call_id
            }))
        elif data_type == 'ice-candidate':
            await self.send_to_target_handler(data)
        elif data_type == 'call-rejected':
            await self.send_to_target_handler(data)
        elif data_type == 'call-answer':
            await self.send_to_target_handler(data)
        elif data_type == 'participant-left':
            await self.send_to_group(data)
        else:
            print(f'Unhandled message type: {data_type}')

    async def send_to_target_handler(self, data):
        await self.channel_layer.group_send(
            self.call_id,
            {
                'type': 'send_to_target',
                'message': data
            }
        )

    async def call_invite_handler(self, data):
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'call_invite',
                'message': data
            }
        )

    async def send_to_target(self, event):
        data = event['message']
        target = data.get('target')
        if target == self.user.username:
            await self.send(text_data=json.dumps(event["message"]))

    async def call_invite(self, event):
        data = event['message']
        target = data.get('target')
        if target == self.user.username:
            self.call_id = data.get('callId')
            await self.channel_layer.group_add(self.call_id, self.channel_name)
            await self.send(text_data=json.dumps(event["message"]))

    async def send_to_group(self, data):
        await self.channel_layer.group_send(
            self.call_id,
            {
                'type': 'send_signal',
                'message': data
            }
        )

    async def send_signal(self, event):
        await self.send(text_data=json.dumps(event["message"]))
