from django.core.management.base import BaseCommand
from inflows.models import ModelInflow
from datetime import date

class Command(BaseCommand):

    def handle(self, *args, **options):
        data = ModelInflow.objects.filter(paid_date__isnull=True, due_date__lte=date.today())
        print(len(data))
        for inflow in data:
            inflow.paid_date = inflow.due_date
            inflow.paid = True
            inflow.save()
