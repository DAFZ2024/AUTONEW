from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def filtrar_por_estado(queryset, estado):
    """Filtrar quejas por estado específico"""
    try:
        return [queja for queja in queryset if queja.estado == estado]
    except:
        return []