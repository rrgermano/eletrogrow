from django import forms
from .models import ModelSupplier

class FormSupplier(forms.ModelForm):
    class Meta:
        model = ModelSupplier
        fields = '__all__'