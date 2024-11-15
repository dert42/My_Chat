from django.db import models
from django.contrib.auth.models import User

class DB_Message(models.Model):
    content = models.TextField()  # Содержимое сообщения
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Содержимое сообщения
    timestamp = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.user.username}: {self.content}"