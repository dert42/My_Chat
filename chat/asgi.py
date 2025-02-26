import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from chat.middleware import TokenAuthMiddleware
from ChatApp import routing as chat_routing
from video_calls import routing as VideoCall_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')
websocket_urlpatterns = chat_routing.application + VideoCall_routing.application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
    )
})
