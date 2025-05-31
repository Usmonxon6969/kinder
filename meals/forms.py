from django import forms
from .models import Meal, MealIngredient, MealServing


class MealForm(forms.ModelForm):
    """Form for creating and updating meals"""

    class Meta:
        model = Meal
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set help texts
        self.fields['name'].help_text = 'Unique name of the meal'
        self.fields['description'].help_text = 'Optional description of the meal'

        # Set description as a text area
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 3})


class MealIngredientForm(forms.ModelForm):
    """Form for adding ingredients to a meal"""

    class Meta:
        model = MealIngredient
        fields = ['ingredient', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set help texts
        self.fields['ingredient'].help_text = 'Select an ingredient'
        self.fields['quantity'].help_text = 'Quantity needed per portion (in grams)'


class MealServingForm(forms.ModelForm):
    """Form for recording meal servings"""

    class Meta:
        model = MealServing
        fields = ['servings', 'notes']

    def __init__(self, *args, **kwargs):
        self.meal = kwargs.pop('meal', None)
        self.max_servings = kwargs.pop('max_servings', 1)
        super().__init__(*args, **kwargs)

        # Set help texts
        self.fields['servings'].help_text = f'Number of portions to serve (max: {self.max_servings})'
        self.fields['notes'].help_text = 'Optional notes about this serving'

        # Set servings min/max
        self.fields['servings'].widget.attrs.update({
            'min': 1,
            'max': self.max_servings,
            'class': 'form-control'
        })

        # Set notes as a text area
        self.fields['notes'].widget = forms.Textarea(attrs={'rows': 3})

    def clean_servings(self):
        """Validate that servings is within the allowed range"""
        servings = self.cleaned_data.get('servings')

        if servings < 1:
            raise forms.ValidationError("Servings must be at least 1")

        if servings > self.max_servings:
            raise forms.ValidationError(f"Maximum allowed servings is {self.max_servings}")

        return servings