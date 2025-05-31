from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Ingredient, IngredientDelivery, IngredientUsage
from common.permissions import IsAdmin, IsManager
from django.db.models import F


class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to require manager or admin role"""

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_manager


@method_decorator(login_required, name='dispatch')
class IngredientListView(ListView):
    model = Ingredient
    template_name = 'ingredients/ingredient_list.html'
    context_object_name = 'ingredients'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        below_threshold = self.request.GET.get('below_threshold')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if below_threshold == '1':
            queryset = queryset.filter(current_quantity__lt=F('threshold_quantity'))

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request  # for form field repopulation
        return context


@method_decorator(login_required, name='dispatch')
class IngredientDetailView(LoginRequiredMixin, DetailView):
    """View ingredient details including usage history"""
    model = Ingredient
    template_name = 'ingredients/ingredient_detail.html'
    context_object_name = 'ingredient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredient = self.get_object()

        # Get recent deliveries
        context['recent_deliveries'] = ingredient.deliveries.order_by('-delivery_date')[:10]

        # Get recent usages
        context['recent_usages'] = ingredient.usages.order_by('-created_at')[:10]

        # Calculate usage stats
        context['total_delivered'] = ingredient.deliveries.aggregate(Sum('quantity'))['quantity__sum'] or 0
        context['total_used'] = ingredient.usages.aggregate(Sum('quantity'))['quantity__sum'] or 0

        return context


@method_decorator(login_required, name='dispatch')
class IngredientCreateView(ManagerRequiredMixin, CreateView):
    """Create a new ingredient - managers and admins only"""
    model = Ingredient
    template_name = 'ingredients/ingredient_form.html'
    fields = ['name', 'current_quantity', 'threshold_quantity', 'unit_price']
    success_url = reverse_lazy('ingredient-list')

    def form_valid(self, form):
        messages.success(self.request, f"Ingredient {form.instance.name} created successfully")
        # Create initial delivery record if quantity > 0
        ingredient = form.save()
        if ingredient.current_quantity > 0:
            IngredientDelivery.objects.create(
                ingredient=ingredient,
                quantity=ingredient.current_quantity,
                created_by=self.request.user,
                notes="Initial inventory"
            )
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class IngredientUpdateView(ManagerRequiredMixin, UpdateView):
    """Update existing ingredient - managers and admins only"""
    model = Ingredient
    template_name = 'ingredients/ingredient_form.html'
    fields = ['name', 'threshold_quantity', 'unit_price']  # Note: current_quantity is handled separately
    success_url = reverse_lazy('ingredient-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Check if threshold changed and might trigger a low inventory alert
        if form.changed_data and 'threshold_quantity' in form.changed_data:
            ingredient = self.object

            # Send WebSocket notification for inventory update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "inventory_updates",
                {
                    'type': 'inventory_update',
                    'ingredient_id': ingredient.id,
                    'ingredient_name': ingredient.name,
                    'current_quantity': ingredient.current_quantity,
                    'threshold_quantity': ingredient.threshold_quantity,
                    'is_below_threshold': ingredient.is_below_threshold
                }
            )

            # If ingredient is below threshold, send low ingredient alert
            if ingredient.is_below_threshold:
                async_to_sync(channel_layer.group_send)(
                    "inventory_updates",
                    {
                        'type': 'low_ingredient_alert',
                        'ingredient_id': ingredient.id,
                        'ingredient_name': ingredient.name,
                        'current_quantity': ingredient.current_quantity,
                        'threshold_quantity': ingredient.threshold_quantity
                    }
                )

        messages.success(self.request, f"Ingredient {form.instance.name} updated successfully")
        return response


@method_decorator(login_required, name='dispatch')
class IngredientDeleteView(ManagerRequiredMixin, DeleteView):
    """Delete existing ingredient - managers and admins only"""
    model = Ingredient
    template_name = 'ingredients/ingredient_confirm_delete.html'
    success_url = reverse_lazy('ingredient-list')

    def delete(self, request, *args, **kwargs):
        ingredient = self.get_object()
        messages.success(request, f"Ingredient {ingredient.name} deleted successfully")
        return super().delete(request, *args, **kwargs)


@login_required
def add_ingredient_quantity(request, pk):
    """Add quantity to an ingredient - managers and admins only"""
    if not (request.user.is_admin or request.user.is_manager):
        messages.error(request, "You don't have permission to perform this action")
        return redirect('ingredient-list')

    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')

        if quantity <= 0:
            messages.error(request, "Please enter a positive quantity")
            return redirect('ingredient-detail', pk=ingredient.pk)

        try:
            new_quantity = ingredient.add_quantity(quantity, request.user)

            # Update the delivery with notes if provided
            if notes:
                delivery = ingredient.deliveries.latest('created_at')
                delivery.notes = notes
                delivery.save()

            # Send WebSocket notification for inventory update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "inventory_updates",
                {
                    'type': 'inventory_update',
                    'ingredient_id': ingredient.id,
                    'ingredient_name': ingredient.name,
                    'current_quantity': new_quantity,
                    'threshold_quantity': ingredient.threshold_quantity,
                    'is_below_threshold': ingredient.is_below_threshold
                }
            )

            # If ingredient is below threshold, send low ingredient alert
            if ingredient.is_below_threshold:
                async_to_sync(channel_layer.group_send)(
                    "inventory_updates",
                    {
                        'type': 'low_ingredient_alert',
                        'ingredient_id': ingredient.id,
                        'ingredient_name': ingredient.name,
                        'current_quantity': new_quantity,
                        'threshold_quantity': ingredient.threshold_quantity
                    }
                )

            messages.success(request, f"Added {quantity}g to {ingredient.name}. New quantity: {new_quantity}g")
            return redirect('ingredient-detail', pk=ingredient.pk)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('ingredient-detail', pk=ingredient.pk)

    return render(request, 'ingredients/add_quantity.html', {'ingredient': ingredient})


@login_required
def get_ingredients_json(request):
    """API endpoint to get all ingredients as JSON"""
    ingredients = Ingredient.objects.all()
    data = [
        {
            'id': ingredient.id,
            'name': ingredient.name,
            'current_quantity': ingredient.current_quantity,
            'threshold_quantity': ingredient.threshold_quantity,
            'is_below_threshold': ingredient.is_below_threshold
        }
        for ingredient in ingredients
    ]
    return JsonResponse(data, safe=False)


@method_decorator(login_required, name='dispatch')
class DeliveryListView(ManagerRequiredMixin, ListView):
    """List all ingredient deliveries - managers and admins only"""
    model = IngredientDelivery
    template_name = 'ingredients/delivery_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by ingredient if provided
        ingredient_id = self.request.GET.get('ingredient')
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)

        return queryset.select_related('ingredient', 'created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all()
        return context