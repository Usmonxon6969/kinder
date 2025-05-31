from django import forms
from .models import Ingredient, IngredientDelivery


class IngredientForm(forms.ModelForm):
    """Form for creating and updating ingredients"""

    class Meta:
        model = Ingredient
        fields = ['name', 'current_quantity', 'threshold_quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)

        if self.is_update:
            # Don't allow direct modification of current_quantity in updates
            # This should be done through deliveries
            self.fields.pop('current_quantity')

        # Set help texts
        self.fields['name'].help_text = 'Unique name of the ingredient'
        self.fields['threshold_quantity'].help_text = 'Minimum quantity (in grams) before alerts are triggered'
        self.fields['unit_price'].help_text = 'Price per kg in local currency'

        if not self.is_update:
            self.fields['current_quantity'].help_text = 'Initial quantity in grams'


class DeliveryForm(forms.ModelForm):
    """Form for recording ingredient deliveries"""

    class Meta:
        model = IngredientDelivery
        fields = ['ingredient', 'quantity', 'delivery_date', 'notes']

    def __init__(self, *args, **kwargs):
        self.ingredient_id = kwargs.pop('ingredient_id', None)
        super().__init__(*args, **kwargs)

        if self.ingredient_id:
            # If an ingredient ID is provided, lock the form to that ingredient
            self.fields['ingredient'].initial = self.ingredient_id
            self.fields['ingredient'].widget = forms.HiddenInput()

        # Set help texts
        self.fields['quantity'].help_text = 'Quantity delivered in grams'
        self.fields['delivery_date'].help_text = 'The date when the delivery was received'
        self.fields['notes'].help_text = 'Optional notes about this delivery (supplier, batch, etc.)'

        # Use date picker widget
        self.fields['delivery_date'].widget = forms.DateInput(attrs={'type': 'date'})