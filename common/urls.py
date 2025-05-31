from django.urls import path
from .views import websocket_test

urlpatterns = [
    path('websocket-test/', websocket_test, name='websocket-test'),
]