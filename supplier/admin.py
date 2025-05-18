from django.contrib import admin
from .models import ModelSupplier

# Register your models here.
@admin.register(ModelSupplier)
class ClientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email',
        'address',
        'neighborhood',
        'city',
        'state',
        'cep',
        'cpf',
        'cnpj'
    )