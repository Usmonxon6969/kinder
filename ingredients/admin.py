from django.contrib import admin
from .models import Ingredient, IngredientDelivery, IngredientUsage


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_quantity', 'threshold_quantity', 'is_below_threshold', 'updated_at')
    list_filter = ('current_quantity', 'threshold_quantity')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def is_below_threshold(self, obj):
        return obj.is_below_threshold

    is_below_threshold.boolean = True
    is_below_threshold.short_description = "Below Threshold"


@admin.register(IngredientDelivery)
class IngredientDeliveryAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'delivery_date', 'created_by', 'created_at')
    list_filter = ('delivery_date', 'created_by')
    search_fields = ('ingredient__name', 'notes')
    date_hierarchy = 'delivery_date'
    readonly_fields = ('created_at',)


@admin.register(IngredientUsage)
class IngredientUsageAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'created_by', 'created_at', 'meal')
    list_filter = ('created_at', 'created_by', 'meal')
    search_fields = ('ingredient__name',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)