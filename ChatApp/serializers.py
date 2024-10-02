from rest_framework import serializers
from ChatApp.models import DB_Message


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = DB_Message
        fields = ['message']
