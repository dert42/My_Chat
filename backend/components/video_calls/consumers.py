import json
import uuid
from abc import ABC, abstractmethod
from channels.generic.websocket import AsyncWebsocketConsumer

from backend.components.video_calls.services.redis_service import RedisService


class Command(ABC):
    """Базовый интерфейс для всех команд."""
    @abstractmethod
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        pass


class CreateCallCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        consumer.call_id = str(uuid.uuid4())
        await consumer.channel_layer.group_add(consumer.call_id, consumer.channel_name)
        #redis = get_redis_connection("default")
        #await redis.sadd(f"call_users:{self.room_id}", self.user.id)
        await consumer.send(text_data=json.dumps({
            'type': 'call-created',
            'target': data.get('target'),
            'from': data.get('from'),
            'callId': consumer.call_id
        }))
        consumer.redis_service.add_user_to_room(consumer.room_id, consumer.user.username)


class CallInviteCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.channel_layer.group_send(
            consumer.room_id,
            {
                'type': 'call_invite',
                'message': data
            }
        )


class IceCandidateCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_target_handler(data)


class CallRejectedCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_target_handler(data)


class CallAnswerCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_target_handler(data)


class ParticipantLeftCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_group_handler(data)
        print(type(data.get('form')))
        print(type(consumer.room_id))
        consumer.redis_service.remove_user_from_room(consumer.room_id, data.get('form'))


class ParticipantJoinedCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_group_handler(data)
        consumer.redis_service.add_user_to_room(consumer.room_id, consumer.user.username)


class CallParticipantCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_group_handler(data)


class CallCreatedCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        await consumer.send_to_group_handler(data)


class GetParticipantCommand(Command):
    async def execute(self, consumer: 'VideoCallConsumer', data: dict):
        participants = consumer.redis_service.get_users_in_room(consumer.room_id)
        participants_decoded = [participant.decode("utf-8") for participant in participants]
        await consumer.send_to_group_handler(data=participants_decoded)


class VideoCallCommandHandler:
    def __init__(self, consumer: 'VideoCallConsumer'):
        self.consumer = consumer
        self.commands: dict[str, Command] = {
            "create-call": CreateCallCommand(),
            "ice-candidate": IceCandidateCommand(),
            "call-invite": CallInviteCommand(),
            "call-answer": CallAnswerCommand(),
            "call-rejected": CallRejectedCommand(),
            "participant-left": ParticipantLeftCommand(),
            "participant-joined": ParticipantJoinedCommand(),
            "call-participants": CallParticipantCommand(),
            "call-created": CallCreatedCommand(),
            "get-participants": GetParticipantCommand(),
            "add-participant": CallInviteCommand()
        }

    async def handle(self, data):
        command = data.get("type")
        if command in self.commands:
            await self.commands[command].execute(data=data, consumer=self.consumer)
        else:
            print(f"Unhandled message type: {data}")


class VideoCallConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.room_id = None
        self.call_id = None
        self.command_handler = VideoCallCommandHandler(consumer=self)
        self.redis_service = RedisService()

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
        await self.command_handler.handle(data)

    async def send_to_target_handler(self, data):
        await self.channel_layer.group_send(
            self.call_id,
            {
                'type': 'send_to_target',
                'message': data
            }
        )

    async def send_to_group_handler(self, data):
        await self.channel_layer.group_send(
            self.call_id,
            {
                'type': 'send_signal',
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

    async def send_signal(self, event):
        print(event)
        await self.send(text_data=json.dumps(event["message"]))
