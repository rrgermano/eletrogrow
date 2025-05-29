from notion.notion_func import get_inflows
from projects.models import ModelProject
from inflows.models import ModelInflow
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        inflows = []
        for income in get_inflows():
            if 'project' in income.keys():
                income['project'] = ModelProject.objects.get(name=income.pop('project'))
            if 'name' in income.keys():
                print(f'name: {income["name"]}')
            inflows.append(ModelInflow(**income))
        ModelInflow.objects.bulk_create(inflows)
