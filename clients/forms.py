from django import forms
from .models import ModelClient

class FormClient(forms.ModelForm):
    class Meta:
        model = ModelClient
        fields = '__all__'