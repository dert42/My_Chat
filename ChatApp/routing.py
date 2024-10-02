from django.urls import re_path
from . import consumers

application = [
    re_path(r'ws/chat', consumers.ChatConsumer.as_asgi())
]
