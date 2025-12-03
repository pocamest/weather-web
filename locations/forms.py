from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class LocationSearchForm(forms.Form):
    query = forms.CharField(
        label='',
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control me-2',
                'type': 'search',
                'placeholder': 'Search',
                'aria-label': 'Search',
            }
        ),
    )


class LocationAddForm(forms.Form):
    name = forms.CharField(label='name', max_length=255)
    country_code = forms.CharField(label='country_code', max_length=2)
    latitude = forms.DecimalField(
        label='latitude',
        max_digits=9,
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = forms.DecimalField(
        label='longitude',
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
