from clients.models import ModelClient
from projects.models import ModelProject
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        clients = ModelClient.objects.all()
        for client in clients:
            if not client.project_prefix:
                actual_prefix = ModelProject.objects.filter(client=client).first()
                if actual_prefix and len(actual_prefix.name) == 6:
                    client.project_prefix = actual_prefix.name[:3]
                    print(client.project_prefix, client)
                client.save()

