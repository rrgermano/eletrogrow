from .models import ModelService, ModelTask
from .serializers import ServiceSerializer, TaskSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

class ListCreateServicesView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelService.objects.all().order_by('-updated_at')
    serializer_class = ServiceSerializer


class RetriveUpdateDestroyServicesView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelService.objects.all().order_by('-updated_at')
    serializer_class = ServiceSerializer 

class ListCreateTasksView(ListCreateAPIView):
    """
    GET /tasks/ - Lista tarefas principais
    POST /tasks/ - Cria tarefa com subtarefas aninhadas
    
    Query params:
    - ?project={id} - Filtra tarefas de um projeto específico (obrigatório para POST)
    - ?completed=true/false - Filtra por status
    - ?created_in_service={id} - Filtra por service de criação
    - ?completed_in_service={id} - Filtra por service de conclusão
    """
    permission_classes = [IsAuthenticated]
    queryset = ModelTask.objects.all()
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por projeto (obrigatório)
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Retorna apenas tarefas principais
        queryset = queryset.filter(parent_task__isnull=True)
        
        # Filtrar por status
        completed = self.request.query_params.get('completed')
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        
        # Filtrar por service de criação
        created_in_service = self.request.query_params.get('created_in_service')
        if created_in_service:
            queryset = queryset.filter(created_in_service_id=created_in_service)
        
        # Filtrar por service de conclusão
        completed_in_service = self.request.query_params.get('completed_in_service')
        if completed_in_service:
            queryset = queryset.filter(completed_in_service_id=completed_in_service)
        
        return queryset.select_related('project', 'created_in_service', 'completed_in_service').prefetch_related('subtasks').order_by('created_at')
    
    def perform_create(self, serializer):
        # O project deve vir no body da requisição
        project_id = self.request.data.get('project')
        if not project_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'project': 'Este campo é obrigatório.'})
        
        # Service de criação é opcional
        created_in_service_id = self.request.data.get('created_in_service')
        created_in_service = None
        if created_in_service_id:
            created_in_service = ModelService.objects.get(id=created_in_service_id)
        
        serializer.save(project_id=project_id, created_in_service=created_in_service)


class RetrieveUpdateDestroyTasksView(RetrieveUpdateDestroyAPIView):
    """
    GET /tasks/{id}/ - Detalhes da tarefa com todas subtarefas
    PUT/PATCH /tasks/{id}/ - Atualiza tarefa e gerencia subtarefas
    DELETE /tasks/{id}/ - Deleta tarefa e todas subtarefas em cascata
    """
    permission_classes = [IsAuthenticated]
    queryset = ModelTask.objects.all()
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        return super().get_queryset().select_related('project', 'created_in_service', 'completed_in_service').prefetch_related('subtasks')