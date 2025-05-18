from django.contrib import admin
from .models import ModelClient

# Register your models here.
@admin.register(ModelClient)
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