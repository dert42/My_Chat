from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('chat/', views.index),
    path('admin/', admin.site.urls),
]
