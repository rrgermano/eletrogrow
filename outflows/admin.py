from django.contrib import admin
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

@admin.register(ModelCreditOutflow)
class OutflowCreditAdmin(admin.ModelAdmin):
    list_display = (
        'expense',
        'favored',
    #    'type',
        'date',
        'project',
        'value',
        'closing',
    )
    filter_horizontal = ('type',)