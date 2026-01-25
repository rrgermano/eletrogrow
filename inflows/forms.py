from django import forms
from .models import ModelInflow

class FormInflow(forms.ModelForm):
    class Meta:
        model = ModelInflow
        fields = '__all__'
        exclude = ['paid_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={'type': 'date'})
                if self.instance and getattr(self.instance, field_name):
                    date_value = getattr(self.instance, field_name)
                    formatted_date = date_value.strftime('%Y-%m-%d')
                    self.initial[field_name] = formatted_date
            if isinstance(field, forms.CheckboxInput):
                field.widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})