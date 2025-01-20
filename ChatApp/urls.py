from django.urls import path
from . import views

urlpatterns = [
    path('chat/list/', views.chat_list, name='chat-list'),
    path('chat/create/', views.create_chat, name='create-chat'),
    path('chat/add_user/', views.add_user, name='add-user'),
    path('chat/delete/<int:room_id>/', views.delete_chat, name='delete-chat'),
]
