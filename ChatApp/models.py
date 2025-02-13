from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class DB_Message(models.Model):
    content = models.TextField()  # Содержимое сообщения
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField()
    def __str__(self):
        return self.content

