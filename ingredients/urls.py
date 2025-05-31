from django.urls import path
from .views import (
    IngredientListView, IngredientDetailView, IngredientCreateView,
    IngredientUpdateView, IngredientDeleteView, DeliveryListView,
    add_ingredient_quantity, get_ingredients_json
)


urlpatterns = [
    path('', IngredientListView.as_view(), name='ingredient-list'),
    path('<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    path('create/', IngredientCreateView.as_view(), name='ingredient-create'),
    path('update/<int:pk>/', IngredientUpdateView.as_view(), name='ingredient-update'),
    path('delete/<int:pk>/', IngredientDeleteView.as_view(), name='ingredient-delete'),
    path('add-quantity/<int:pk>/', add_ingredient_quantity, name='add-ingredient-quantity'),
    path('json/', get_ingredients_json, name='ingredients-json'),
    path('deliveries/', DeliveryListView.as_view(), name='delivery-list'),
]