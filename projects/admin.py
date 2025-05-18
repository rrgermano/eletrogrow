from django.contrib import admin
from .models import ModelProject

# Register your models here.
@admin.register(ModelProject)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'client',
        'start_project',
        'start_work',
        'end_project',
        'parcel',
        'value',
        'due_date',
    )