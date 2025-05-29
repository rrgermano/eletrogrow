from notion.notion_func import get_suppliers
from supplier.models import ModelSupplier
from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    def handle(self, *args, **options):
        suppliers = []
        for supplier in get_suppliers():
            
            suppliers.append(ModelSupplier(**supplier))
        ModelSupplier.objects.bulk_create(
            suppliers, 
            update_conflicts=True, 
            unique_fields=['name'], 
            update_fields=[
                'phone',
                'email',
                'address',
                'neighborhood',
                'city',
                'state',
                'cpf',
                'cnpj',
                'cep',
            ]
        )
