from django.contrib import admin
from .models import Meal, MealIngredient, MealServing


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'get_ingredient_count', 'max_possible_portions')
    search_fields = ('name', 'description')
    inlines = [MealIngredientInline]
    readonly_fields = ('created_at', 'updated_at')

    def get_ingredient_count(self, obj):
        return obj.ingredients.count()

    get_ingredient_count.short_description = "Ingredients"


@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    list_display = ('meal', 'ingredient', 'quantity')
    list_filter = ('meal', 'ingredient')
    search_fields = ('meal__name', 'ingredient__name')
    autocomplete_fields = ['meal', 'ingredient']


@admin.register(MealServing)
class MealServingAdmin(admin.ModelAdmin):
    list_display = ('meal', 'serving_date', 'served_by', 'servings')
    list_filter = ('serving_date', 'served_by', 'meal')
    search_fields = ('meal__name', 'notes')
    date_hierarchy = 'serving_date'
    readonly_fields = ('serving_date',)