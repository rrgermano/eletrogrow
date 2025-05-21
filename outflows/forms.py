from typing import Any
from django import forms
from supplier.models import ModelSupplier
from .models import OutflowTypeChoice, ModelOutflow, ModelCreditOutflow
from projects.models import ModelProject
from django.utils.timezone import now

METHOD_CHOICES =[
    ('PIX', 'PIX'),
    ('CRED', 'Cartão de crédito'),
    ('DEB', 'Cartão de débito'),
    ('BOL', 'Boleto'),
    ('REF', 'Reembolso'),
    ('AUT', 'Débito Automático'),
]

class FormOutflow(forms.Form):
    expense = forms.CharField(max_length=50, label='Despesa')
    favored = forms.ModelChoiceField(queryset=ModelSupplier.objects.all(), blank=True, required=False, label='Favorecido')
    paid = forms.BooleanField(label='Pago', required=False, initial=False)
    type = forms.ModelMultipleChoiceField(queryset=OutflowTypeChoice.objects.all(), blank=True, required=False, widget=forms.CheckboxSelectMultiple, label='Tipo', to_field_name=None)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data',)
    payment_method = forms.ChoiceField(choices=METHOD_CHOICES, label='Método de pagamento', initial='CRED')
    project = forms.ModelChoiceField(queryset=ModelProject.objects.all(), blank=True, label='Projeto', required=False,)
    parcel = forms.IntegerField(label='Parcelas', initial=1)
    value = forms.FloatField(label='Valor')

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None) 
        super().__init__(*args, **kwargs)
        if self.instance:
            # Preenche os campos com os dados da instância para UpdateView
            self.fields['expense'].initial = self.instance.expense
            self.fields['favored'].initial = self.instance.favored
            self.fields['paid'].initial = self.instance.paid
            self.fields['type'].initial = self.instance.type.all()  # Para ManyToMany
            self.fields['date'].initial = self.instance.date.strftime('%Y-%m-%d')
            self.fields['payment_method'].initial = self.instance.payment_method
            self.fields['project'].initial = self.instance.project
            self.fields['parcel'].initial = self.instance.parcel if hasattr(self.instance, 'parcel') else None
            self.fields['value'].initial = self.instance.value
        else:
            last_related_outflow = ModelOutflow.objects.order_by('-id').first()
            last_related_credit = ModelCreditOutflow.objects.order_by('-id').first()
            if last_related_outflow and last_related_credit:
                if last_related_outflow.update_time.timestamp() > last_related_credit.update_time.timestamp():
                    self.fields['project'].initial = last_related_outflow.project
                else:
                    self.fields['project'].initial = last_related_credit.project
            elif last_related_outflow:
                self.fields['project'].initial = last_related_outflow.project
            elif last_related_credit:
                self.fields['project'].initial = last_related_credit.project
            self.fields['date'].initial = now().strftime('%Y-%m-%d')
    def clean_type(self):
        types = self.cleaned_data.get('type')
        if types:
            return list(types)
        return []