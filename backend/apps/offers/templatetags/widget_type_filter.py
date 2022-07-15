from django import template
from django.forms import CheckboxInput
from django_select2.forms import Select2MultipleWidget

register = template.Library()

@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput)

@register.filter(name='is_select2widget')
def is_select2widget(value):
    return isinstance(value, Select2MultipleWidget)