import django_filters
import googlemaps
import logging
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

    

class ChildcareFilter(OfferFilter):
    class Meta:
        model = ChildcareOffer
        fields = ['helpType_childcare', "timeOfDay", "numberOfChildren","isRegular"]
        filter_overrides = FILTER_OVERRIDES


class JobFilter(OfferFilter):
    class Meta:
        model = JobOffer
        fields = ['jobType']
        filter_overrides = FILTER_OVERRIDES

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
        
class WelfareFilter(OfferFilter):
    class Meta:
        model = WelfareOffer
        fields = ['helpType', 'hasEducation_welfare']
        filter_overrides = FILTER_OVERRIDES

class TransportationFilter(OfferFilter):
    date = django_filters.DateFilter(widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    class Meta:
        model = TransportationOffer
        fields = [ 'numberOfPassengers','distance', 'helpType', 'typeOfCar']
        filter_overrides = FILTER_OVERRIDES

class TranslationFilter(OfferFilter):

    #languages = django_filters.ModelMultipleChoiceFilter(widget=s2forms.Select2MultipleWidget(), conjoined=True)
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