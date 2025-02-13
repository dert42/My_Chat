import logging
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import ProfilePicture
from .serializers import RegisterSerializer


logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Создание токена для нового пользователя
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': RegisterSerializer(user).data,
            'token': token.key[0]
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token = Token.objects.get_or_create(user=user)
            print('Вход: ', token)
            print(user)
            return Response({'token': token[0].key})
        return Response({'error': 'Invalid Credentials'}, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # Получаем токен пользователя
            token = Token.objects.get(user=request.user)
            # Удаляем токен, чтобы завершить сеанс
            token.delete()
            return Response({'message': 'Logged out successfully'}, status=200)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=400)


class ProfilePictureViewSet(APIView):
    parser_classes = [MultiPartParser]  # Позволяет загружать файлы
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if "avatar" not in request.FILES:
            logger.error("Файл не передан в запросе")
            return Response({"error": "Файл не передан"}, status=status.HTTP_400_BAD_REQUEST)

        profile, created = ProfilePicture.objects.get_or_create(user=user)
        # Проверяем, передаётся ли файл
        uploaded_file = request.FILES["avatar"]
        logger.info(f"Файл получен: {uploaded_file.name}, размер: {uploaded_file.size} байт")

        # Сохраняем файл
        profile.profile_picture = uploaded_file
        profile.save()
        logger.info(f"Файл сохранён в S3: {profile.profile_picture.name}")

        return Response({"avatar_url": profile.get_avatar_url()}, status=status.HTTP_201_CREATED)

    def get(self, request):
        try:
            profile_picture = get_object_or_404(ProfilePicture, user_id=request.user.id)
            return Response({
                'username': request.user.username,
                "avatar_url": profile_picture.get_avatar_url()
            })
        except Http404:
            return Response({
                'username': request.user.username,
                "avatar_url": None
            })
