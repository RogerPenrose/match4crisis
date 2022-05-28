import django_filters
import googlemaps
from math import cos, radians
from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms
from django_select2 import forms as s2forms
from apps.accounts.models import Languages
from .models import GenericOffer, JobOffer, ChildcareOffer,  WelfareOffer, TranslationOffer, TransportationOffer, BuerocraticOffer, ManpowerOffer, AccommodationOffer

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

class GenericFilter(django_filters.FilterSet):
    cost_lt = django_filters.NumberFilter(field_name="cost", lookup_expr="lt")
    created_at = django_filters.ChoiceFilter(choices=DATE_CHOICES, method=date_select_filter, label=_("Zeitraum"), empty_label=_("Zeitraum wählen"))
    class Meta:
        model = GenericOffer
        fields = ["created_at"]

class LocationFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(method="filter_location", label="", widget=forms.TextInput(attrs={'placeholder': _("Gib hier einen Standort ein")}))
    radius = django_filters.ChoiceFilter(choices=RADIUS_CHOICES, method='no_filter', label=_("Umkreis"), empty_label=None)

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
        return queryset.filter(lat__range=(latMin,latMax), lng__range=(lngMin,lngMax))

    

class ChildcareFilter(django_filters.FilterSet):
    class Meta:
        model = ChildcareOffer
        fields = ['helpType_childcare', "timeOfDay", "numberOfChildren","isRegular"]


class JobFilter(django_filters.FilterSet):
    class Meta:
        model = JobOffer
        fields = ['jobType']

class BuerocraticFilter(django_filters.FilterSet):
    class Meta:
        model = BuerocraticOffer
        fields = ['helpType']
        
class ManpowerFilter(django_filters.FilterSet):
    class Meta:
        model = ManpowerOffer
        fields = ['distanceChoices', 'canGoforeign', 'hasDriverslicense', 'hasMedicalExperience', 'hasExperience_crisis']
class AccommodationFilter(django_filters.FilterSet):
    
    startDateAccommodation = django_filters.DateFilter(widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    class Meta:
        model = AccommodationOffer
        fields = ['numberOfPeople', 'petsAllowed', 'typeOfResidence', 'startDateAccommodation' ]
        
class WelfareFilter(django_filters.FilterSet):
    class Meta:
        model = WelfareOffer
        fields = ['helpType', 'hasEducation_welfare']
class TransportationFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    class Meta:
        model = TransportationOffer
        fields = [ 'numberOfPassengers','distance', 'helpType', 'typeOfCar']
class TranslationFilter(django_filters.FilterSet):
    class Meta:
        model = TranslationOffer
        fields = ['languages' ]


# TODO when adding new offer types this needs to be updated
OFFER_FILTERS = {
    'AC' : AccommodationFilter,
    'TL' : TranslationFilter,
    'TR' : TransportationFilter,
    'BU' : BuerocraticFilter,
    'CL' : ChildcareFilter,
    'WE' : WelfareFilter,
    'MP' : ManpowerFilter,
    'JO' : JobFilter,
}