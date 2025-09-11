from notion.notion_func import get_projects
from clients.models import ModelClient
from projects.models import ModelProject
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = []
        projects_name = []
        for project in get_projects():
            project['client'] = ModelClient.objects.get(name=project.pop('client'))
            projects.append(ModelProject(**project))
            projects_name.append(project['name'])
        for name in projects_name:
            if projects_name.count(name) > 1:
                print(f'Projeto: {name} vezes: {projects_name.count(name)}')
        ModelProject.objects.bulk_create(projects, ignore_conflicts=True)

        missing = set([p.name for p in projects]) - set(ModelProject.objects.values_list("name", flat=True))
        if missing:
            print("Esses não foram criados:", missing)
            