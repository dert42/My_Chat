from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated


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
            print(token)
            print(request.user)
            # Удаляем токен, чтобы завершить сеанс
            token.delete()
            return Response({'message': 'Logged out successfully'}, status=200)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=400)