from django import template
from django.apps import apps

register = template.Library()

@register.filter
def has_attr(obj, name):
    return hasattr(obj, name)

@register.filter
def has_field(queryset, field_name):
    """
    Verifica se o modelo de um queryset tem um campo específico
    Uso: {% if outflows|model_has_field:"paid" %}
    """
    if not queryset:
        return False
    
    # Pega o modelo do primeiro objeto
    model = queryset.model if hasattr(queryset, 'model') else queryset[0].__class__
    
    try:
        model._meta.get_field(field_name)
        return True
    except:
        return False