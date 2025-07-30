from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import ModelCreditOutflow, ModelOutflow
from inflows.models import ModelInflow

REFUND_TAX = 25

@receiver(m2m_changed, sender=ModelCreditOutflow.type.through)
def refund_credit_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        outflow_type = instance.type.filter(name='Reembolso')
        if outflow_type and instance.project:
            name = instance.expense.split(' - ')
            if len(name)>1:
                if name[1].split('/')[0] != '1':
                    return
                parcels = int(name[1].split('/')[1])
                value = instance.value*parcels
                income=name[0]
            else:
                value = instance.value
                income = name[0]

            ModelInflow.objects.create(
                income = income,
                value = value*(1+REFUND_TAX/100),
                project = instance.project,
                due_date = instance.project.due_date,
                refund=True,
            )

@receiver(m2m_changed, sender=ModelOutflow.type.through)
def refund_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        outflow_type = instance.type.filter(name='Reembolso')
        if outflow_type and instance.project:
            ModelInflow.objects.create(
                income = instance.expense,
                value = instance.value*(1+REFUND_TAX/100),
                project = instance.project,
                due_date = instance.project.due_date,
                refund=True,
            )