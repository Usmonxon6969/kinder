from django import forms
from datetime import datetime


class ReportGenerationForm(forms.Form):
    """Form for generating monthly reports"""
    year = forms.IntegerField(
        min_value=2020,
        max_value=datetime.now().year,
        required=True,
        help_text='Select the year for the report'
    )

    month = forms.IntegerField(
        min_value=1,
        max_value=12,
        required=True,
        help_text='Select the month for the report'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_year = datetime.now().year
        current_month = datetime.now().month

        # Set initial values to current year and month
        self.fields['year'].initial = current_year
        self.fields['month'].initial = current_month

        # Set widgets
        self.fields['year'].widget = forms.Select(choices=[(y, y) for y in range(2020, current_year + 1)])
        self.fields['month'].widget = forms.Select(choices=[
            (1, 'January'), (2, 'February'), (3, 'March'),
            (4, 'April'), (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'), (9, 'September'),
            (10, 'October'), (11, 'November'), (12, 'December')
        ])

    def clean(self):
        """Validate that the selected month and year are not in the future"""
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')

        if year and month:
            current_date = datetime.now()

            if year > current_date.year or (year == current_date.year and month > current_date.month):
                raise forms.ValidationError("You cannot generate reports for future periods")

        return cleaned_data