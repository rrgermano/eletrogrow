

def project_name(client, klass):
    projects = klass.objects.filter(client=client)
    if projects:
        project_serie = int(max([project.name.removeprefix(client.project_prefix) for project in projects])) + 1
    else:
        project_serie = 0
    name = f'{client.project_prefix}{project_serie:03}'
    return name
