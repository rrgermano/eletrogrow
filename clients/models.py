from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.br.models import BRCPFField, BRCNPJField, BRPostalCodeField, BRStateField
from django.core.exceptions import ValidationError
from .acronym import get_project_prefix


class ModelClient(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name='Nome')
    phone = PhoneNumberField(blank=True, null=True, region='BR', verbose_name='Telefone')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    address = models.CharField(blank=True, null=True, verbose_name='Endereço')
    neighborhood = models.CharField(blank=True, null=True, verbose_name='Bairro')
    city = models.CharField(blank=True, null=True, verbose_name='Cidade')
    state = BRStateField(blank=True, null=True, verbose_name='Estado')
    cep = BRPostalCodeField(blank=True, null=True, verbose_name='CEP')
    cpf = BRCPFField(blank=True, null=True, verbose_name='CPF')
    cnpj = BRCNPJField(blank=True, null=True, verbose_name='CNPJ')
    project_prefix = models.CharField(max_length=3, blank=True, null=True, unique=True, verbose_name='Prefixo de projeto')

    def clean(self):
        super().clean()
        if self.cpf and self.cnpj:
            raise ValidationError('Informe apenas CPF ou CNPJ, não ambos')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.project_prefix:
            exceptions = set()
            prefix = get_project_prefix(self.name, exceptions)
            colisions = ModelClient.objects.filter(project_prefix=prefix).first()
            while colisions:
                exceptions.add(colisions.project_prefix)
                prefix = get_project_prefix(self.name, exceptions)
                colisions = ModelClient.objects.filter(project_prefix=prefix).first()
            self.project_prefix = prefix
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
