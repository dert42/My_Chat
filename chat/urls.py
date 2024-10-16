from django.urls import path, include

urlpatterns = [
    path('', include('ChatApp.urls')),
    path('', include('accounts.urls'))
]
