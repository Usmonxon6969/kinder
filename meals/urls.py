from django.urls import path
from .views import (
    MealListView, MealDetailView, MealCreateView,
    MealUpdateView, MealDeleteView, MealServingListView,
    serve_meal, get_meals_json
)


urlpatterns = [
    path('', MealListView.as_view(), name='meal-list'),
    path('<int:pk>/', MealDetailView.as_view(), name='meal-detail'),
    path('create/', MealCreateView.as_view(), name='meal-create'),
    path('update/<int:pk>/', MealUpdateView.as_view(), name='meal-update'),
    path('delete/<int:pk>/', MealDeleteView.as_view(), name='meal-delete'),
    path('serve/<int:pk>/', serve_meal, name='serve-meal'),
    path('servings/', MealServingListView.as_view(), name='serving-list'),
    path('json/', get_meals_json, name='meals-json'),
]