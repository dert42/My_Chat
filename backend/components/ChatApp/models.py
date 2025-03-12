from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, through='Room_users')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'ChatApp'


class Room_users(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        app_label = 'ChatApp'

class DB_Message(models.Model):
    content = models.TextField()  # Содержимое сообщения
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    class Meta:
        app_label = 'ChatApp'


