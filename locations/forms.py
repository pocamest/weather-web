from django import forms


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
