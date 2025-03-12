from rest_framework import serializers
from .models import Room, DB_Message
from django.contrib.auth.models import User


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'users']


class DBMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DB_Message
        fields = ['id', 'content', 'room', 'user', 'timestamp']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
