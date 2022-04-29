import django_filters as filters
import operator
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from functools import reduce

from .models import DonationRequest

DATE_CHOICES = (
    (0, _("Heute")),
    (7, _("Letzte Woche")),
    (30, _("Letzte 30 Tage")),
    (90, _("Letzte 90 Tage")),
    (365, _("Letztes Jahr"))
)

class DonationRequestFilter(filters.FilterSet):
    search = filters.CharFilter(method="custom_filter", label=_("Suchen"))
    createdAt = filters.ChoiceFilter(choices=DATE_CHOICES, method="date_select_filter", label=_("Zeitraum"), empty_label=_("Keine Begrenzung"))

    def custom_filter(self, queryset, name, value):
        values = value.split(" ")
        return queryset.filter(
            Q(description__icontains=value) | 
            reduce(operator.or_, ((Q(organisation__organisationName__icontains=val) | Q(title__icontains=val)) for val in values))
        )
    
    def date_select_filter(self, queryset, name, value):
        """Filter for dates inside the last <value> days"""
        value = int(value)
        lookup = '__'.join((name, 'gte'))
        return queryset.filter(**{lookup: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(value)})
