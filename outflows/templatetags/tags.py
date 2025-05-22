from django import template

register = template.Library()

@register.filter
def has_attr(obj, name):
    return hasattr(obj, name)

@register.filter
def has_field(queryset, field_name):
    if not queryset:
        return False
    model = queryset.model if hasattr(queryset, 'model') else queryset[0].__class__
    
    try:
        model._meta.get_field(field_name)
        return True
    except:
        return False