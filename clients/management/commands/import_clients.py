from notion.notion_func import get_clients
from clients.models import ModelClient
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        for client in get_clients():
            print(client['name'])
            obj, created = ModelClient.objects.update_or_create(**client)

            print(f'Nome: {obj.name}, Criado {created}')

