from notion.notion_func import get_credit_outflows
from projects.models import ModelProject
from outflows.models import ModelCreditOutflow, OutflowTypeChoice
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for expense in get_credit_outflows():
            if 'project' in expense.keys() and expense['project']:
                expense['project'] = ModelProject.objects.get(name=expense.pop('project'))
            types = expense.pop('type')
            outflow = ModelCreditOutflow(**expense)
            outflow.save()
            if types:
                for type in types:
                    object_type = OutflowTypeChoice.objects.get_or_create(name=type)[0].pk
                    outflow.type.add(object_type)
