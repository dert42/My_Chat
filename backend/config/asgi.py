import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from backend.config.middleware import TokenAuthMiddleware
from backend.components.ChatApp import routing as chat_routing
from backend.components.video_calls import routing as VideoCall_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
websocket_urlpatterns = chat_routing.application + VideoCall_routing.application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
    )
})
