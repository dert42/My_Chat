import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from chat.middleware import TokenAuthMiddleware
from ChatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddleware(
            URLRouter(
                routing.application
            )
    )
})
