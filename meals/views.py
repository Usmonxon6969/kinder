from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.db.models import Sum, Count
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Meal, MealIngredient, MealServing
from ingredients.models import Ingredient
from common.permissions import IsAdmin, IsManager


class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to require manager or admin role"""

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager


@method_decorator(login_required, name='dispatch')
class MealListView(LoginRequiredMixin, ListView):
    model = Meal
    template_name = 'meals/meal_list.html'
    context_object_name = 'meals'
    paginate_by = 20

    def get_queryset(self):
        base_qs = super().get_queryset().select_related('created_by').prefetch_related('ingredients__ingredient')

        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        sort = self.request.GET.get('sort')

        if name:
            base_qs = base_qs.filter(name__icontains=name)

        if sort == 'newest':
            base_qs = base_qs.order_by('-created_at')
        else:
            base_qs = base_qs.order_by('name')

        # Save as list only AFTER sorting and filtering
        meals = list(base_qs)

        # Apply availability filter last, in-memory
        if status == 'available':
            meals = [m for m in meals if m.can_be_served()[0]]
        elif status == 'unavailable':
            meals = [m for m in meals if not m.can_be_served()[0]]

        return meals


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for meal in context['meals']:
            meal.possible_portions = meal.max_possible_portions()
            meal.can_be_served_now, meal.can_be_served_message = meal.can_be_served()

        context['request'] = self.request  # allows templates to repopulate form fields
        return context



@method_decorator(login_required, name='dispatch')
class MealDetailView(LoginRequiredMixin, DetailView):
    """View meal details including ingredients and serving history"""
    model = Meal
    template_name = 'meals/meal_detail.html'
    context_object_name = 'meal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal = self.get_object()

        # Calculate portions
        context['max_portions'] = meal.max_possible_portions()
        context['can_be_served'], context['serve_message'] = meal.can_be_served()

        # Get recent servings
        context['recent_servings'] = meal.servings.order_by('-serving_date')[:10]

        # Calculate total servings
        total_servings = meal.servings.aggregate(total=Sum('servings'))
        context['total_servings'] = total_servings['total'] or 0

        return context


@method_decorator(login_required, name='dispatch')
class MealCreateView(ManagerRequiredMixin, CreateView):
    """Create a new meal - managers and admins only"""
    model = Meal
    template_name = 'meals/meal_form.html'
    fields = ['name', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['ingredients_formset'] = self.get_ingredients_formset(self.request.POST)
        else:
            context['ingredients_formset'] = self.get_ingredients_formset()

        context['ingredients'] = Ingredient.objects.all()
        return context

    def get_ingredients_formset(self, data=None):
        MealIngredientFormSet = inlineformset_factory(
            Meal, MealIngredient,
            fields=('ingredient', 'quantity'),
            extra=1, can_delete=True
        )
        return MealIngredientFormSet(data=data, instance=self.object, prefix='ingredients')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Save the ingredients formset
        ingredients_formset = self.get_ingredients_formset(self.request.POST)
        ingredients_formset.instance = self.object

        if ingredients_formset.is_valid():
            ingredients_formset.save()
            messages.success(self.request, f"Meal {form.instance.name} created successfully")
        else:
            # If formset is invalid, delete the meal and show errors
            self.object.delete()
            for error in ingredients_formset.errors:
                messages.error(self.request, error)
            return self.form_invalid(form)

        return response

    def get_success_url(self):
        return reverse('meal-detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class MealUpdateView(ManagerRequiredMixin, UpdateView):
    """Update existing meal - managers and admins only"""
    model = Meal
    template_name = 'meals/meal_form.html'
    fields = ['name', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['ingredients_formset'] = self.get_ingredients_formset(self.request.POST)
        else:
            context['ingredients_formset'] = self.get_ingredients_formset()

        context['ingredients'] = Ingredient.objects.all()
        return context

    def get_ingredients_formset(self, data=None):
        MealIngredientFormSet = inlineformset_factory(
            Meal, MealIngredient,
            fields=('ingredient', 'quantity'),
            extra=1, can_delete=True
        )
        return MealIngredientFormSet(data=data, instance=self.object, prefix='ingredients')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Save the ingredients formset
        ingredients_formset = self.get_ingredients_formset(self.request.POST)

        if ingredients_formset.is_valid():
            ingredients_formset.save()
            messages.success(self.request, f"Meal {form.instance.name} updated successfully")
        else:
            for error in ingredients_formset.errors:
                messages.error(self.request, error)
            return self.form_invalid(form)

        return response

    def get_success_url(self):
        return reverse('meal-detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class MealDeleteView(ManagerRequiredMixin, DeleteView):
    """Delete existing meal - managers and admins only"""
    model = Meal
    template_name = 'meals/meal_confirm_delete.html'
    success_url = reverse_lazy('meal-list')

    def delete(self, request, *args, **kwargs):
        meal = self.get_object()
        messages.success(request, f"Meal {meal.name} deleted successfully")
        return super().delete(request, *args, **kwargs)


@login_required
def serve_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)

    if request.method == 'POST':
        servings = int(request.POST.get('servings', 1))
        notes = request.POST.get('notes', '')

        if servings <= 0:
            messages.error(request, "Please enter a positive number of servings")
            return redirect('meal-detail', pk=meal.pk)

        can_serve, message = meal.can_be_served()
        if not can_serve:
            messages.error(request, f"Cannot serve this meal: {message}")
            return redirect('meal-detail', pk=meal.pk)

        try:
            meal_serving = meal.serve(request.user, servings=servings)

            if notes:
                meal_serving.notes = notes
                meal_serving.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "meal_servings",
                {
                    'type': 'meal_served',
                    'meal_id': meal.id,
                    'meal_name': meal.name,
                    'servings': servings,
                    'served_by': request.user.username,
                    'timestamp': meal_serving.serving_date.isoformat()
                }
            )

            for m in Meal.objects.all():
                max_portions = m.max_possible_portions()
                async_to_sync(channel_layer.group_send)(
                    "meal_servings",
                    {
                        'type': 'portions_update',
                        'meal_id': m.id,
                        'meal_name': m.name,
                        'max_portions': max_portions
                    }
                )

            messages.success(request, f"Successfully served {servings} portion(s) of {meal.name}")
            return redirect('meal-detail', pk=meal.pk)
        except Exception as e:
            messages.error(request, f"Error serving meal: {str(e)}")
            return redirect('meal-detail', pk=meal.pk)

    return render(request, 'meals/serve_meal.html', {
        'meal': meal,
        'max_portions': meal.max_possible_portions()
    })


@method_decorator(login_required, name='dispatch')
class MealServingListView(LoginRequiredMixin, ListView):
    """List all meal servings"""
    model = MealServing
    template_name = 'meals/serving_list.html'
    context_object_name = 'servings'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by meal if provided
        meal_id = self.request.GET.get('meal')
        if meal_id:
            queryset = queryset.filter(meal_id=meal_id)

        # Filter by date range if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(serving_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(serving_date__lte=end_date)

        return queryset.select_related('meal', 'served_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meals'] = Meal.objects.all()
        return context


@login_required
def get_meals_json(request):
    """API endpoint to get all meals as JSON with their max portions"""
    meals = Meal.objects.all()
    data = [
        {
            'id': meal.id,
            'name': meal.name,
            'max_portions': meal.max_possible_portions(),
            'can_be_served': meal.can_be_served()[0],
            'ingredient_count': meal.ingredients.count()
        }
        for meal in meals
    ]
    return JsonResponse(data, safe=False)