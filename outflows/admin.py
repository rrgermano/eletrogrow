from django.contrib import admin
from django import forms
from .models import ModelOutflow, ModelCreditOutflow, OutflowTypeChoice

@admin.register(OutflowTypeChoice)
class OutflowTypeChoicesAdmin(admin.ModelAdmin):
    pass

@admin.register(ModelOutflow)
class OutflowAdmin(admin.ModelAdmin):
    list_display = (
        'expense',
        'favored',
        'paid',
#        'type',
        'date',
        'payment_method',
        'project',
        'value',
    )
    filter_horizontal = ('type',)

# @admin.register(ModelCreditOutflow)
# class OutflowCreditAdmin(admin.ModelAdmin):
#     list_display = (
#         'expense',
#         'favored',
#     #    'type',
#         'date',
#         'project',
#         'value',
#         'closing',
#     )
#     filter_horizontal = ('type',)

class CreditOutflowAdminForm(forms.ModelForm):
    installments = forms.IntegerField(
        label='Número de Parcelas',
        initial=1,
        min_value=1,
        max_value=120,
        required=False,
        help_text='Deixe em branco ou 1 para pagamento à vista'
    )

    class Meta:
        model = ModelCreditOutflow
        fields = '__all__'


@admin.register(ModelCreditOutflow)
class CreditOutflowAdmin(admin.ModelAdmin):
    form = CreditOutflowAdminForm
    list_display = ['expense', 'favored', 'date', 'value', 'closing']
    list_filter = ['closing', 'date', 'favored']
    search_fields = ['expense', 'favored__name']

    def save_model(self, request, obj, form, change):
        """Override para suportar parcelamento no admin"""
        if not change:  # Apenas na criação
            num_installments = form.cleaned_data.get('installments', 1)
            types_list = form.cleaned_data.get('type', [])

            # Gera parcelas
            obj.generate_installments(num_installments, list(types_list))
        else:
            # Edição normal
            super().save_model(request, obj, form, change)