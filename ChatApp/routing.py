from django.urls import re_path
from . import consumers

application = [
    re_path(r'ws/chat/(?P<room_name>[^/]+)/', consumers.ChatConsumer.as_asgi())
]
