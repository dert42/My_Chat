from django.contrib.auth.models import User
from rest_framework import serializers

from rest_framework import serializers
from .models import ProfilePicture


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProfilePictureSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfilePicture
        fields = ["id", "user", "profile_picture", "avatar_url"]
        extra_kwargs = {"profile_picture": {"write_only": True}}  # Не показываем сам файл в ответе

    def get_avatar_url(self, obj):
        print('URLE*RURUKKLRUKj       ', obj.get_avatar_url())
        return obj.get_avatar_url()
