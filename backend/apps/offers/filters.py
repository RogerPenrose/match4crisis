import django_filters
import googlemaps
import logging
import json
from math import cos, radians
from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms
from django_select2 import forms as s2forms
from apps.accounts.models import Languages
from .models import GenericOffer, JobOffer, ChildcareOffer,  WelfareOffer, TranslationOffer, TransportationOffer, BuerocraticOffer, ManpowerOffer, AccommodationOffer

gmaps = googlemaps.Client(key='AIzaSyAuyDEd4WZh-OrW8f87qmS-0sSrY47Bblk')
logger = logging.getLogger("django")


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

FILTER_OVERRIDES = {
    models.BooleanField: {
        'filter_class': django_filters.BooleanFilter,
        'extra': lambda f: {
            'widget': forms.CheckboxInput(attrs={'class':'form-control', 'value' : 'true'}),
        },
    },
    models.IntegerField: {
        'filter_class': django_filters.NumberFilter,
        'extra': lambda f: {
            'widget': forms.NumberInput(attrs={'class':'form-control'}),
        },
    },
}   

def date_select_filter(queryset, name, value):
    """Filter for dates inside the last <value> days"""
    value = int(value)
    lookup = '__'.join((name, 'gte'))
    return queryset.filter(**{lookup: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(value)})


class OfferFilter(django_filters.FilterSet):
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)

        # Apply custom class attributes to the selects 
        # Necessary as long as https://github.com/carltongibson/django-filter/issues/1475 isn't resolved
        for f in self.filters.values():
            if isinstance(f, django_filters.ChoiceFilter):
                f.extra.update({'widget': forms.Select(attrs={'class' : 'form-control'})})

class GenericFilter(django_filters.FilterSet):
    cost_lt = django_filters.NumberFilter(field_name="cost", lookup_expr="lt")
    created_at = django_filters.ChoiceFilter(choices=DATE_CHOICES, method=date_select_filter, label=_("Zeitraum"), empty_label=_("Zeitraum wählen"))
    class Meta:
        model = GenericOffer
        fields = ["created_at"]

class ChildcareFilter(OfferFilter):
    class Meta:
        model = ChildcareOffer
        fields = {
            "helpType_childcare" : ['exact'],
            "timeOfDay" : ['exact'], 
            "numberOfChildren" : ['gte'],
            "isRegular" : ['exact'],
            "hasExperience" : ['exact'],
            "hasEducation" : ['exact'],
            "hasSpace" : ['exact'],
        }
        filter_overrides = FILTER_OVERRIDES

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['numberOfChildren__gte'].label = _("Anzahl Kinder (mindestens)")
        self.filters['isRegular'].label = _("Reguläre Betreuung gewünscht")
        self.filters['hasExperience'].label = _("Sollte Erfahrung haben")
        self.filters['hasEducation'].label = _("Sollte Ausbildung haben")
        self.filters['hasSpace'].label = _("Sollte Räumlichkeiten bei sich haben")

class JobFilter(OfferFilter):
    jobType = django_filters.MultipleChoiceFilter(widget=s2forms.Select2MultipleWidget, choices=JobOffer.JOB_CHOICES)
    class Meta:
        model = JobOffer
        fields = ['jobType']
        #filter_overrides = FILTER_OVERRIDES

class BuerocraticFilter(OfferFilter):
    class Meta:
        model = BuerocraticOffer
        fields = ['helpType']
        filter_overrides = FILTER_OVERRIDES
        
class ManpowerFilter(OfferFilter):
    class Meta:
        model = ManpowerOffer
        fields = ['distanceChoices', 'canGoforeign', 'hasDriverslicense', 'hasMedicalExperience', 'hasExperience_crisis']
        filter_overrides = FILTER_OVERRIDES

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['hasDriverslicense'].label = _("Sollte Fahrerlaubnis haben")
        self.filters['hasMedicalExperience'].label = _("Sollte medizinische Erfahrung haben")
        self.filters['hasExperience_crisis'].label = _("Sollte Erfahrung mit Krisenmanagement haben")

class AccommodationFilter(OfferFilter):
    
    startDateAccommodation__gte = django_filters.DateFilter("startDateAccommodation", "gte", widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    class Meta:
        model = AccommodationOffer
        fields = {
            'numberOfPeople' : ['gte'], 
            'petsAllowed' : ['exact'], 
            'typeOfResidence' : ['exact'], 
            'startDateAccommodation' : ['gte']
        }
        filter_overrides = FILTER_OVERRIDES

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['numberOfPeople__gte'].label = _("Personenanzahl (mindestens)")
        self.filters['startDateAccommodation__gte'].label = _("Startdatum der Unterbringung")
        
class WelfareFilter(OfferFilter):
    class Meta:
        model = WelfareOffer
        fields = ['helpType', 'hasEducation_welfare']
        filter_overrides = FILTER_OVERRIDES
    
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['hasEducation_welfare'].label = _("Sollte medizinische Vorerfahrung haben")

class TransportationFilter(OfferFilter):
    #distance = django_filters.ChoiceFilter(choices=TransportationOffer.)
    class Meta:
        model = TransportationOffer
        fields = { 
            'numberOfPassengers' : ['gte'],
            'distance' : ['exact'], 
            'helpType' : ['exact'], 
            'typeOfCar' : ['exact']
            }
        filter_overrides = FILTER_OVERRIDES

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['numberOfPassengers__gte'].label = _("Anzahl freier Plätze (mindestens)")

class TranslationFilter(OfferFilter):

    class Meta:
        model = TranslationOffer
        fields = ['languages']
        filter_overrides = {
            models.ManyToManyField : {
            'filter_class' : django_filters.ModelMultipleChoiceFilter,
            'extra': lambda f: {
                'widget': s2forms.Select2MultipleWidget,
                'queryset' : django_filters.filterset.remote_queryset(f),
                'conjoined' : True
            },
        }
        }


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