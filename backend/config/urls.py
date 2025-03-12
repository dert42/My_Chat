from django.urls import path, include

urlpatterns = [
    path('', include('components.accounts.urls')),
    path('', include('components.ChatApp.urls')),
]
