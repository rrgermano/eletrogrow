from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ModelProject
from inflows.models import ModelInflow
from dateutil.relativedelta import relativedelta
from app.utils import is_date_util

@receiver(post_save, sender=ModelProject)
def project_installment(sender, instance, **kwargs):
    inflows = ModelInflow.objects.filter(income__startswith=instance.name)
    if inflows:
        for income in inflows:
            income.delete()
    created_ids = []
    parcel_value = instance.value/instance.parcel
    for parcel in range(instance.parcel):
        inflow = ModelInflow.objects.create(
            income=f'{instance.name} - {parcel+1}/{instance.parcel}',
            project=instance,
            due_date=is_date_util(instance.due_date + relativedelta(months=parcel)),
            value=parcel_value,
        )
        created_ids.append(inflow.id)
    instance.inflows.exclude(id__in=created_ids).update(due_date=is_date_util(instance.due_date))



