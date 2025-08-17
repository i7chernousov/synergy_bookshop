from django import forms
from .models import OrderItem

class RentalForm(forms.Form):
    duration = forms.ChoiceField(choices=OrderItem.Duration.choices, label='Срок аренды')
