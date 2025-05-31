from django.contrib import admin
from .models import MonthlyReport, ReportIngredientUsage, ReportMealServing


class ReportIngredientUsageInline(admin.TabularInline):
    model = ReportIngredientUsage
    extra = 0
    readonly_fields = ('ingredient_name', 'quantity_used', 'quantity_delivered', 'discrepancy')
    can_delete = False


class ReportMealServingInline(admin.TabularInline):
    model = ReportMealServing
    extra = 0
    readonly_fields = ('meal_name', 'servings_count', 'total_ingredients_used')
    can_delete = False


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('period_label', 'total_meals_served', 'total_servings',
                    'discrepancy_rate', 'high_discrepancy', 'generated_at')
    list_filter = ('year', 'month', 'high_discrepancy')
    readonly_fields = ('year', 'month', 'generated_at', 'generated_by',
                       'total_meals_served', 'total_servings', 'total_potential_servings',
                       'discrepancy_rate', 'total_ingredients_used', 'total_ingredients_delivered',
                       'high_discrepancy')
    inlines = [ReportIngredientUsageInline, ReportMealServingInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False