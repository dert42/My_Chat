from django.conf import settings
import redis


class RedisService:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def add_user_to_room(self, room_name, username):
        self.client.sadd(room_name, username)

    def remove_user_from_room(self, room_name: str, username: str):
        self.client.srem(room_name, username)

    def get_users_in_room(self, room_name):
        return self.client.smembers(room_name)
