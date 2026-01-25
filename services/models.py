from django.db import models
from projects.models import ModelProject
from django.utils.timezone import now

OS_TYPE_CHOICES = [
    ('COR', 'Corrido'),
    ('CONT', 'Contratado'),
]

OS_STATUS_CHOICES = [
    ('OPEN', 'Aberto'),
    ('CLOSED', 'Fechado'),
    ('APROV', 'Aprovado'),
    ('WIP', 'Em Andamento'),
    ('CANC', 'Cancelado'),
    ('WAR', 'Garantia')
]
# Create your models here.
class ModelService(models.Model):
    project = models.ForeignKey(ModelProject, on_delete=models.CASCADE, related_name='services_projects', verbose_name='Projeto')
    service_type = models.CharField(choices=OS_TYPE_CHOICES, default='COR', verbose_name='Tipo de Serviço')
    description = models.TextField(verbose_name='Descriçao do serviço')
    closing = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    status = models.CharField(choices=OS_STATUS_CHOICES, default='OPEN', verbose_name='Status')

    def __str__(self):
        return f'#{self.pk}'

class ModelDisplacement(models.Model):
    service = models.ForeignKey(ModelService, related_name='displacements', on_delete=models.CASCADE, verbose_name='Serviço')
    name = models.CharField(max_length=100, verbose_name='Name')
    departure_time = models.TimeField(verbose_name='Partida', blank=True, null=True)
    arrive_time = models.TimeField(verbose_name='Chegada', blank=True, null=True)
    distance = models.FloatField(verbose_name='Distance', blank=True, null=True)
    description = models.TextField(verbose_name='Descrição', blank=True, null=True)

    class Meta:
        verbose_name = 'Deslocamento'

    def __str__(self):
        return f'{self.service} - {self.name}'

class ModelTask(models.Model):
    description = models.TextField(verbose_name="Descrição")
    completed = models.BooleanField(default=False, verbose_name="Completa")
    
    # Relacionamento com Project (tarefa pertence ao projeto)
    project = models.ForeignKey(
        ModelProject,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Projeto"
    )
    
    # Service onde a tarefa foi criada
    created_in_service = models.ForeignKey(
        ModelService,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_created',
        verbose_name="Criada no Serviço"
    )
    
    # Service onde a tarefa foi completada
    completed_in_service = models.ForeignKey(
        ModelService,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_completed',
        verbose_name="Completada no Serviço"
    )
    
    # Relacionamento recursivo - uma tarefa pode ter uma tarefa pai
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name="Tarefa Pai"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completada em")
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['created_at']
    
    def __str__(self):
        level = self.get_level()
        prefix = "  " * level + ("└─ " if level > 0 else "")
        status = "✓" if self.completed else "○"
        return f"{prefix}[{status}] {self.description[:50]}"
    
    def get_level(self):
        """Retorna o nível de profundidade da tarefa (0 = raiz)"""
        level = 0
        current_task = self
        while current_task.parent_task:
            level += 1
            current_task = current_task.parent_task
        return level
    
    def all_subtasks_completed(self):
        """Verifica se todas as subtarefas diretas estão completas"""
        subtasks = self.subtasks.all()
        if not subtasks.exists():
            return True
        return all(sub.completed for sub in subtasks)
    
    def update_automatic_status(self):
        """
        Atualiza o status da tarefa baseado nas subtarefas.
        Se todas as subtarefas estiverem completas, marca como completa.
        """
        if self.subtasks.exists():
            should_be_completed = self.all_subtasks_completed()
            if self.completed != should_be_completed:
                self.completed = should_be_completed
                if should_be_completed and not self.completed_at:
                    self.completed_at = now()
                elif not should_be_completed:
                    self.completed_at = None
                    self.completed_in_service = None
                self.save(update_fields=['completed', 'completed_at', 'completed_in_service'])
            
            # Propaga para cima (atualiza a tarefa pai também)
            if self.parent_task:
                self.parent_task.update_automatic_status()
    
    def mark_completed(self, value=True, service=None):
        """
        Marca a tarefa como completa/incompleta.
        Se marcar como incompleta, desmarca todas as subtarefas também.
        """
        
        self.completed = value
        
        if value:
            if not self.completed_at:
                self.completed_at = now()
            if service:
                self.completed_in_service = service
        else:
            self.completed_at = None
            self.completed_in_service = None
        
        self.save(update_fields=['completed', 'completed_at', 'completed_in_service'])
        
        if not value:
            # Se desmarcar, desmarca todas as subtarefas recursivamente
            for subtask in self.subtasks.all():
                subtask.mark_completed(False)
        else:
            # Se marcar como completa, atualiza a tarefa pai
            if self.parent_task:
                self.parent_task.update_automatic_status()
    
    def get_all_subtasks_recursive(self):
        """Retorna todas as subtarefas em todos os níveis"""
        subtasks = list(self.subtasks.all())
        for subtask in list(subtasks):
            subtasks.extend(subtask.get_all_subtasks_recursive())
        return subtasks
    
    def get_progress(self):
        """Retorna o progresso em porcentagem (0-100)"""
        all_tasks = self.get_all_subtasks_recursive()
        if not all_tasks:
            return 100 if self.completed else 0
        
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.completed)
        return int((completed / total) * 100)
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para evitar loops infinitos
        (uma tarefa não pode ser pai de si mesma)
        """
        if self.parent_task:
            # Verifica se está tentando criar um loop
            current_task = self.parent_task
            while current_task:
                if current_task.pk == self.pk:
                    raise ValueError("Uma tarefa não pode ser subtarefa de si mesma!")
                current_task = current_task.parent_task
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['created_at']
    
    def __str__(self):
        level = self.get_level()
        prefix = "  " * level + ("└─ " if level > 0 else "")
        status = "✓" if self.completed else "○"
        return f"{prefix}[{status}] {self.description[:50]}"
    
    def get_level(self):
        """Retorna o nível de profundidade da tarefa (0 = raiz)"""
        level = 0
        current_task = self
        while current_task.parent_task:
            level += 1
            current_task = current_task.parent_task
        return level
    
    def all_subtasks_completed(self):
        """Verifica se todas as subtarefas diretas estão completas"""
        subtasks = self.subtasks.all()
        if not subtasks.exists():
            return True
        return all(sub.completed for sub in subtasks)
    
    def update_automatic_status(self):
        """
        Atualiza o status da tarefa baseado nas subtarefas.
        Se todas as subtarefas estiverem completas, marca como completa.
        """
        if self.subtasks.exists():
            self.completed = self.all_subtasks_completed()
            self.save(update_fields=['completed'])
            
            # Propaga para cima (atualiza a tarefa pai também)
            if self.parent_task:
                self.parent_task.update_automatic_status()
    
    def mark_completed(self, value=True):
        """
        Marca a tarefa como completa/incompleta.
        Se marcar como incompleta, desmarca todas as subtarefas também.
        """
        self.completed = value
        self.save(update_fields=['completed'])
        
        if not value:
            # Se desmarcar, desmarca todas as subtarefas recursivamente
            for subtask in self.subtasks.all():
                subtask.mark_completed(False)
        else:
            # Se marcar como completa, atualiza a tarefa pai
            if self.parent_task:
                self.parent_task.update_automatic_status()
    
    def get_all_subtasks_recursive(self):
        """Retorna todas as subtarefas em todos os níveis"""
        subtasks = list(self.subtasks.all())
        for subtask in list(subtasks):
            subtasks.extend(subtask.get_all_subtasks_recursive())
        return subtasks
    
    def get_progress(self):
        """Retorna o progresso em porcentagem (0-100)"""
        all_tasks = self.get_all_subtasks_recursive()
        if not all_tasks:
            return 100 if self.completed else 0
        
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.completed)
        return int((completed / total) * 100)
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para evitar loops infinitos
        (uma tarefa não pode ser pai de si mesma)
        """
        if self.parent_task:
            # Verifica se está tentando criar um loop
            current_task = self.parent_task
            while current_task:
                if current_task.pk == self.pk:
                    raise ValueError("Uma tarefa não pode ser subtarefa de si mesma!")
                current_task = current_task.parent_task
        
        super().save(*args, **kwargs)