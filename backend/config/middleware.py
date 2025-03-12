from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
import urllib.parse

@database_sync_to_async
def get_user_from_token(key):
    try:
        token = Token.objects.get(key=key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Извлекаем токен из параметров URL
        query_string = scope.get('query_string', b'').decode('utf-8')
        params = urllib.parse.parse_qs(query_string)
        token_key = params.get('token', [None])[0]

        if token_key:
            scope["user"] = await get_user_from_token(token_key)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
