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
    type = forms.ModelMultipleChoiceField(queryset=OutflowTypeChoice.objects.all(), blank=True, required=False, widget=forms.CheckboxSelectMultiple, label='Tipo')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data',)
    payment_method = forms.ChoiceField(choices=METHOD_CHOICES, label='Método de pagamento', initial='CRED')
    project = forms.ModelChoiceField(queryset=ModelProject.objects.all(), blank=True, label='Projeto', required=False,)
    parcel = forms.IntegerField(label='Parcelas', initial=1)
    value = forms.FloatField(label='Valor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
