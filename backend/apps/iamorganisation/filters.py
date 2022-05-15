from math import cos, radians
from django import forms
import django_filters as filters
import operator
import googlemaps
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from functools import reduce

gmaps = googlemaps.Client(key='AIzaSyAuyDEd4WZh-OrW8f87qmS-0sSrY47Bblk')

DATE_CHOICES = (
    (0, _("Heute")),
    (7, _("Letzte Woche")),
    (30, _("Letzte 30 Tage")),
    (90, _("Letzte 90 Tage")),
    (365, _("Letztes Jahr"))
)

RADIUS_CHOICES = (
    (5, _("5km")),
    (10, _("10km")),
    (20, _("20km")),
    (50, _("50km")),
    (100, _("100km")),
)


def date_select_filter(queryset, name, value):
    """Filter for dates inside the last <value> days"""
    value = int(value)
    lookup = '__'.join((name, 'gte'))
    return queryset.filter(**{lookup: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(value)})



class DonationRequestFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter", label="", widget=forms.TextInput(attrs={'placeholder': _("Suchen")}))
    createdAt = filters.ChoiceFilter(choices=DATE_CHOICES, method=date_select_filter, label=_("Zeitraum"), empty_label=_("Zeitraum wählen"))

    def search_filter(self, queryset, name, value):
        values = value.split(" ")
        return queryset.filter(
            Q(description__icontains=value) | 
            reduce(operator.or_, ((Q(organisation__organisationName__icontains=val) | Q(title__icontains=val)) for val in values))
        )
    
class HelpRequestFilter(filters.FilterSet):

    search = filters.CharFilter(method="search_filter", label=_("Suchen"), widget=forms.TextInput(attrs={'placeholder': _("Suchen")}))
    location = filters.CharFilter(method="filter_location", label=_("Ort"))
    radius = filters.ChoiceFilter(choices=RADIUS_CHOICES, method='no_filter', label=_("Umkreis"), empty_label=None)
    createdAt = filters.ChoiceFilter(choices=DATE_CHOICES, method=date_select_filter, label=_("Zeitraum"), empty_label=_("Zeitraum wählen"))

    def search_filter(self, queryset, name, value):
        values = value.split(" ")
        return queryset.filter(
            Q(description__icontains=value) | 
            reduce(operator.or_, ((Q(organisation__organisationName__icontains=val) | Q(title__icontains=val)) for val in values))
        )

    def no_filter(self, queryset, name, value):
        return queryset

    def filter_location(self, queryset, name, value):
        gc = gmaps.geocode(value)
        latVal = gc[0]['geometry']['location']['lat']
        lngVal = gc[0]['geometry']['location']['lng']
        radiusKM = int(self.data['radius'])
        latMin = latVal - radiusKM/110.574
        latMax = latVal + radiusKM/110.574
        lngDist = cos(radians(latVal)) * 111.320
        lngMin = lngVal - radiusKM/lngDist
        lngMax = lngVal + radiusKM/lngDist
        return queryset.filter(lat__gte=latMin, lat__lte=latMax, lng__gte=lngMin, lng__lte=lngMax)