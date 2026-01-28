from rest_framework import serializers
from .models import ModelService, ModelDisplacement, ModelTask

class DisplacementSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    departure_time = serializers.TimeField(required=False)
    arrive_time = serializers.TimeField(required=False)
    class Meta:
        model = ModelDisplacement
        fields = [
            'id',
            'name',
            'departure_time',
            'arrive_time',
            'distance',
            'description',
        ]

    def to_internal_value(self, data):
        for field in ('departure_time', 'arrive_time'):
            if data.get(field) == "":
                data[field] = None
        return super().to_internal_value(data)


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer recursivo completo para criar/atualizar/deletar tarefas
    com subtarefas aninhadas em qualquer profundidade
    """
    id = serializers.IntegerField(required=False)
    subtasks = serializers.SerializerMethodField(read_only=False)
    level = serializers.IntegerField(source='get_level', read_only=True)
    progress = serializers.IntegerField(source='get_progress', read_only=True)
    subtasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelTask
        fields = [
            'id',
            'description',
            'completed',
            'level',
            'progress',
            'subtasks_count',
            'subtasks',
            'created_in_service',
            'completed_in_service',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at','completed_in_service',  'created_in_service']
    
    def get_subtasks(self, obj):
        """Retorna todas as subtarefas de forma recursiva"""
        subtasks = obj.subtasks.all().order_by('created_at')
        return TaskSerializer(subtasks, many=True).data
    
    def get_subtasks_count(self, obj):
        return obj.subtasks.count()
    
    def to_internal_value(self, data):
        """
        Converte os dados de entrada, permitindo subtarefas aninhadas
        """
        # Processa subtarefas recursivamente
        if 'subtasks' in data:
            subtasks_data = data.pop('subtasks')
            internal = super().to_internal_value(data)
            internal['subtasks'] = subtasks_data
            return internal
        return super().to_internal_value(data)
    
    def _create_subtasks(self, parent_task, subtasks_data, project, created_in_service=None):
        """Cria subtarefas recursivamente garantindo o mesmo project"""
        for subtask_data in subtasks_data:
            # Remove subtarefas aninhadas para processar depois
            nested_subtasks_data = subtask_data.pop('subtasks', [])
            
            # Cria a subtarefa com o project da tarefa principal
            subtask = ModelTask.objects.create(
                parent_task=parent_task,
                project=project,
                created_in_service=created_in_service,
                **subtask_data
            )
            
            # Cria as subtarefas dela recursivamente
            if nested_subtasks_data:
                self._create_subtasks(subtask, nested_subtasks_data, project, created_in_service)
    
    def _manage_subtasks(self, parent_task, subtasks_data, project, current_service=None):
        """Gerencia criação/atualização/deleção de subtarefas recursivamente"""
        existing = {st.id: st for st in parent_task.subtasks.all()}
        received_ids = set()
        
        for subtask_data in subtasks_data:
            subtask_id = subtask_data.pop('id', None)
            nested_subtasks_data = subtask_data.pop('subtasks', None)
            
            if subtask_id and subtask_id in existing:
                # UPDATE - atualiza subtarefa existente
                obj = existing[subtask_id]
                old_completed = obj.completed
                
                for attr, value in subtask_data.items():
                    setattr(obj, attr, value)
                
                # Se mudou para completa e não tinha completed_in_service, registra
                if not old_completed and obj.completed and not obj.completed_in_service and current_service:
                    obj.completed_in_service = current_service
                
                obj.save()
                received_ids.add(subtask_id)
                
                # Gerencia as subtarefas dela recursivamente
                if nested_subtasks_data is not None:
                    self._manage_subtasks(obj, nested_subtasks_data, project, current_service)
                
                # Atualiza status automático
                obj.update_automatic_status()
            else:
                # CREATE - cria nova subtarefa com o project correto
                obj = ModelTask.objects.create(
                    parent_task=parent_task,
                    project=project,
                    created_in_service=current_service,
                    **subtask_data
                )
                received_ids.add(obj.id)
                
                # Cria as subtarefas dela recursivamente
                if nested_subtasks_data:
                    self._create_subtasks(obj, nested_subtasks_data, project, current_service)
        
        # DELETE - remove subtarefas que não foram enviadas
        to_delete = set(existing.keys()) - received_ids
        if to_delete:
            ModelTask.objects.filter(id__in=to_delete).delete()


class ServiceSerializer(serializers.ModelSerializer):
    costumer_name = serializers.ReadOnlyField(source='project.client.name')
    project_name = serializers.ReadOnlyField(source='project.name')
#    value = serializers.ReadOnlyField(source='project.value')
    displacements = DisplacementSerializer(many=True, required=False)
    tasks = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = ModelService
        fields = [
            'id',
            'project',
            'project_name',
            'costumer_name',
            'service_type',
            'description',
            'closing',
            'date',
            'updated_at',
            'status',
#               'value',
            'displacements',
            'tasks',
        ]
    
    def get_tasks(self, obj):
        """Retorna apenas tarefas principais do projeto deste service"""
        main_tasks = ModelTask.objects.filter(
            project=obj.project,
            parent_task__isnull=True
        ).order_by('created_at')
        return TaskSerializer(main_tasks, many=True).data
    
    def to_internal_value(self, data):
        """
        Converte os dados de entrada, permitindo tasks e displacements aninhados
        """
        # Processa tasks
        if 'tasks' in data:
            tasks_data = data.pop('tasks')
            internal = super().to_internal_value(data)
            internal['tasks'] = tasks_data
            return internal
        return super().to_internal_value(data)

    def create(self, validated_data):
        displacements_data = validated_data.pop('displacements', [])
        tasks_data = validated_data.pop('tasks', [])
        
        service = ModelService.objects.create(**validated_data)
        
        # Cria displacements
        ModelDisplacement.objects.bulk_create([
            ModelDisplacement(service=service, **displacement)
            for displacement in displacements_data
        ])
        
        # Cria tasks (vinculadas ao project, não ao service)
        # Cria ou atualiza tasks (pertencem ao projeto, não ao service)
        task_serializer = TaskSerializer()

        existing_tasks = {
            t.id: t
            for t in ModelTask.objects.filter(
                project=service.project,
                parent_task__isnull=True
            )
        }

        for task_data in tasks_data:
            task_id = task_data.pop('id', None)
            subtasks_data = task_data.pop('subtasks', [])

            if task_id and task_id in existing_tasks:
                # UPDATE
                task = existing_tasks[task_id]
                old_completed = task.completed

                for attr, value in task_data.items():
                    setattr(task, attr, value)

                if not old_completed and task.completed and not task.completed_in_service:
                    task.completed_in_service = service

                task.save()

                if subtasks_data:
                    task_serializer._manage_subtasks(
                        task,
                        subtasks_data,
                        service.project,
                        service
                    )

                task.update_automatic_status()

            else:
                # CREATE
                task = ModelTask.objects.create(
                    project=service.project,
                    created_in_service=service,
                    parent_task=None,
                    **task_data
                )

                if subtasks_data:
                    task_serializer._create_subtasks(
                        task,
                        subtasks_data,
                        service.project,
                        service
                    )

                task.update_automatic_status()

        
        return service
    
    def update(self, instance, validated_data):
        displacements_data = validated_data.pop('displacements', None)
        tasks_data = validated_data.pop('tasks', None)
        
        # Atualiza campos do service
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Gerencia displacements
        if displacements_data is not None:
            existing = {d.id: d for d in instance.displacements.all()}
            received_ids = set()
            
            for displacement_data in displacements_data:
                displacement_id = displacement_data.pop('id', None)
                
                if displacement_id and displacement_id in existing:
                    # UPDATE
                    obj = existing[displacement_id]
                    for attr, value in displacement_data.items():
                        setattr(obj, attr, value)
                    obj.save()
                    received_ids.add(displacement_id)
                else:
                    # CREATE
                    obj = ModelDisplacement.objects.create(
                        service=instance,
                        **displacement_data
                    )
                    received_ids.add(obj.id)
            
            # DELETE
            to_delete = set(existing.keys()) - received_ids
            if to_delete:
                ModelDisplacement.objects.filter(id__in=to_delete).delete()
        
        # Gerencia tasks do projeto (tasks pertencem ao projeto, não ao service)
        if tasks_data is not None:
            existing = {
                t.id: t 
                for t in ModelTask.objects.filter(
                    project=instance.project,
                    parent_task__isnull=True
                )
            }
            received_ids = set()
            task_serializer = TaskSerializer()
            
            for task_data in tasks_data:
                task_id = task_data.pop('id', None)
                subtasks_data = task_data.pop('subtasks', None)
                
                if task_id and task_id in existing:
                    # UPDATE
                    obj = existing[task_id]
                    old_completed = obj.completed
                    
                    for attr, value in task_data.items():
                        setattr(obj, attr, value)
                    
                    # Se foi marcada como completa agora, registra o service
                    if not old_completed and obj.completed and not obj.completed_in_service:
                        obj.completed_in_service = instance
                    
                    obj.save()
                    received_ids.add(task_id)
                    
                    # Gerencia subtarefas recursivamente
                    if subtasks_data is not None:
                        task_serializer._manage_subtasks(obj, subtasks_data, instance.project, instance)
                    
                    # Atualiza status automático baseado nas subtarefas
                    obj.update_automatic_status()
                else:
                    # CREATE - nova task para o projeto
                    obj = ModelTask.objects.create(
                        project=instance.project,
                        created_in_service=instance,
                        parent_task=None,
                        **task_data
                    )
                    received_ids.add(obj.id)
                    
                    # Cria subtarefas recursivamente
                    if subtasks_data:
                        task_serializer._create_subtasks(obj, subtasks_data, instance.project, instance)
                    
                    # Atualiza status automático baseado nas subtarefas
                    obj.update_automatic_status()
            
            # DELETE - remove apenas tarefas principais não enviadas (CASCADE deleta as subtarefas)
            to_delete = set(existing.keys()) - received_ids
            if to_delete:
                ModelTask.objects.filter(id__in=to_delete).delete()
        
        return instance