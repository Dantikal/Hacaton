from django import template

register = template.Library()

@register.filter
def status_color(status):
    colors = {
        'todo': 'secondary',
        'in_progress': 'info',
        'done': 'success'
    }
    return colors.get(status, 'secondary')

@register.filter
def split_comma(value):
    """Разделяет строку по запятым"""
    return value.split(',')

@register.filter
def strip(value):
    return value.strip()
