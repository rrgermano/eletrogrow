from notion.notion_func import get_outflows
from projects.models import ModelProject
from outflows.models import ModelOutflow, OutflowTypeChoice, METHOD_CHOICES
from supplier.models import ModelSupplier
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for expense in get_outflows():
            if 'project' in expense.keys() and expense['project']:
                expense['project'] = ModelProject.objects.get(name=expense.pop('project'))
            if 'favored' in expense.keys() and expense['favored']:
                expense['favored'] = ModelSupplier.objects.get(name=expense.pop('favored'))
            if expense['payment_method']:
                for method in METHOD_CHOICES:
                    if expense['payment_method'].lower() == method[1].lower():
                        expense['payment_method'] = method[0]
                        break
            types = expense.pop('type')
            outflow = ModelOutflow(**expense)
            outflow.save()
            if types:
                for type in types:
                    object_type = OutflowTypeChoice.objects.get_or_create(name=type)[0].pk
                    outflow.type.add(object_type)
