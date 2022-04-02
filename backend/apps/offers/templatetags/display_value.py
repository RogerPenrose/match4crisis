import logging
from django import template

register = template.Library()
logger = logging.getLogger("django")
@register.filter(name='display')
def display_value(boundField):
    """
    Returns field's data or it's verbose version 
    for a field with choices defined.

    Usage::

        {% load data_verbose %}
        {{form.some_field|data_verbose}}
    """
    data = boundField.data
    field = boundField.field
    return hasattr(field, 'choices') and dict(field.choices).get(data,'') or data