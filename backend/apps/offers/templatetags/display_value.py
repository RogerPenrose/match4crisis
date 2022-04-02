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
    widget = field.widget
    logger.warning("DATA: "+str(data) + "FIELD "+ str(field.widget.__dict__))
    return hasattr(widget, 'choices') and dict(widget.choices).get(data,'') or data