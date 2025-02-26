from django.urls import re_path
from . import consumers

application = [
    re_path(r'ws/call/', consumers.VideoCallConsumer.as_asgi())
]
