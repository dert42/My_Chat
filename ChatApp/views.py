from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect

def index(request):
    return render(request, '../templates/main/index.html')


def send_message_to_clients(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'your_group_name',
        {'type': 'send_message', 'message': message}
    )
