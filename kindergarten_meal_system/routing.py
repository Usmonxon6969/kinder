from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/inventory/$', consumers.InventoryConsumer.as_asgi()),
    re_path(r'ws/meal-servings/$', consumers.MealServingConsumer.as_asgi()),
]