from django import template
from django.conf import settings

register = template.Library()

@register.filter
def getdictvalue(dict, key):
    """Gets a dict entry dynamically from a string name"""
    if key in dict:
        return dict[key]
    elif hasattr(dict, '__getitem__'):
        return dict.__getitem__(key)
    else:
        return None
