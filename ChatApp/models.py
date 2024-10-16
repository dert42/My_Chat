from django.db import models


class DB_Message(models.Model):
    content = models.TextField()  # Содержимое сообщения
