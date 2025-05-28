from django import forms
from .models import Wine
from datetime import datetime

class WineForm(forms.ModelForm):
    class Meta:
        model = Wine
        current_year = datetime.now().year
        fields = ['winename', 'producer', 'country', 'region', 'year', 'winetype', 'grapes', 'purchase', 'dealer',
                  'price', 'drinkfrom', 'drinkto', 'warehouse', 'notes', 'nmbrbottles', 'wine_image']

        labels = {
            'winename': 'Wine name',
            'producer': 'Producer',
            'winetype': 'Wine type',
            'grapes': 'Grapes',
            'year': 'Vintage',
            'country': 'Country',
            'region': 'Region',
            'purchase': 'Purchase date',
            'price': 'Price (~EUR)',
            'dealer': 'Merchant',
            'drinkfrom': 'Drinkable from',
            'drinkto': 'Drinkable until',
            'warehouse': 'Storage location',
            'nmbrbottles': 'Number of bottles',
            'wine_image': 'Wine image'
        }

        widgets = {
            'winename': forms.TextInput(attrs={'class': "form-control"}),
            'producer': forms.TextInput(attrs={'class': "form-control"}),
            'grapes': forms.TextInput(attrs={'class': "form-control"}),
            'winetype': forms.Select(attrs={'class': "form-control"}),
            'year': forms.NumberInput(attrs={'class': "form-control", 'min': '1990', 'max': '2025'}),
            'country': forms.Select(attrs={'class': "form-control"}),
            'region': forms.TextInput(attrs={'class': "form-control"}),
            'purchase': forms.DateInput(format=('%Y-%m-%d'), attrs={"type": "date", 'class': "form-control"}),
            'price': forms.TextInput(attrs={'class': "form-control"}),
            'dealer': forms.TextInput(attrs={'class': "form-control"}),
            'notes': forms.Textarea(attrs={'class': "form-control", 'cols': 100, 'rows': 5}),
            'drinkfrom': forms.NumberInput(attrs={'class': "form-control", 'min': '2000', 'max': '2060'}),
            'drinkto': forms.NumberInput(attrs={'class': "form-control", 'min': '2018', 'max': '2060'}),
            'warehouse': forms.TextInput(attrs={'class': "form-control"}),
            'nmbrbottles': forms.NumberInput(attrs={'class': "form-range", 'type': 'range', 'min': '0', 'max': '18'}),
            'wine_image': forms.FileInput(attrs={'class': "form-control"})
        }
