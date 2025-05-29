from django.contrib import admin
from .models import ModelInflow

# Register your models here.
@admin.register(ModelInflow)
class InflowAdmin(admin.ModelAdmin):
    list_display = (
        'income',
        'paid',
        'project',
        'due_date',
        'payment_method',
        'value',
        'refund',
    )