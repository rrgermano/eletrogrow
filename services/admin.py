from django.contrib import admin
from .models import ModelService, ModelDisplacement, ModelTask

# Register your models here.
@admin.register(ModelService)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'service_type',
        'description',
        'closing',
        'date',
        'updated_at',
        'status',
    ]

@admin.register(ModelDisplacement)
class DisplacementAdmin(admin.ModelAdmin):
    list_display = [
        'service',
        'name',
        'departure_time',
        'arrive_time',
        'distance',
        'description',
    ]

class SubtaskInline(admin.TabularInline):
    model = ModelTask
    fk_name = 'parent_task'
    extra = 0
    fields = ['description', 'completed', 'created_at', 'completed_at']
    readonly_fields = ['created_at', 'completed_at']
    verbose_name = "Subtarefa"
    verbose_name_plural = "Subtarefas"
    show_change_link = True


@admin.register(ModelTask)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'description_short', 
        'project', 
        'completed', 
        'level_display',
        'progress_display',
        'created_in_service',
        'completed_in_service',
        'created_at'
    ]
    
    list_filter = [
        'completed',
        'project',
        'created_in_service',
        'completed_in_service',
        'created_at',
    ]
    
    search_fields = [
        'description',
        'project__name',
    ]
    
    readonly_fields = [
        'level_display',
        'progress_display',
        'created_at',
        'updated_at',
        'completed_at',
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('description', 'completed', 'project', 'parent_task')
        }),
        ('Rastreamento de Services', {
            'fields': ('created_in_service', 'completed_in_service')
        }),
        ('Métricas', {
            'fields': ('level_display', 'progress_display')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SubtaskInline]
    
    def description_short(self, obj):
        """Descrição truncada com indicador de nível"""
        prefix = "  " * obj.get_level() + ("└─ " if obj.get_level() > 0 else "")
        return f"{prefix}{obj.description[:50]}"
    description_short.short_description = "Descrição"
    
    def level_display(self, obj):
        return obj.get_level()
    level_display.short_description = "Nível"
    
    def progress_display(self, obj):
        return f"{obj.get_progress()}%"
    progress_display.short_description = "Progresso"
    
    def get_queryset(self, request):
        """Otimiza queries"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'project',
            'parent_task',
            'created_in_service',
            'completed_in_service'
        ).prefetch_related('subtasks')
    
    actions = ['mark_as_completed', 'mark_as_incomplete']
    
    def mark_as_completed(self, request, queryset):
        """Action para marcar tasks como completas"""
        for task in queryset:
            task.mark_completed(True)
        self.message_user(request, f"{queryset.count()} tarefa(s) marcada(s) como completa(s).")
    mark_as_completed.short_description = "Marcar como completa"
    
    def mark_as_incomplete(self, request, queryset):
        """Action para marcar tasks como incompletas"""
        for task in queryset:
            task.mark_completed(False)
        self.message_user(request, f"{queryset.count()} tarefa(s) marcada(s) como incompleta(s).")
    mark_as_incomplete.short_description = "Marcar como incompleta"