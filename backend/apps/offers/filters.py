import django_filters
from django.db import models
from django import forms
from django_select2 import forms as s2forms
from apps.accounts.models import Languages
from .models import GenericOffer, JobOffer, ChildcareOffer,  WelfareOffer, TranslationOffer, TransportationOffer, DonationOffer, BuerocraticOffer, ManpowerOffer, AccommodationOffer
class GenericFilter(django_filters.FilterSet):
    cost_lt = django_filters.NumberFilter(field_name="cost", lookup_expr="lt")
    class Meta:
        model = GenericOffer
        fields = ['offerType',"lat","lng"]

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
        fields = ['helpType_buerocratic']
        
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
        fields = ['helpType_welfare', 'hasEducation_welfare']
class TransportationFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    class Meta:
        model = TransportationOffer
        fields = [ 'numberOfPassengers','distance', 'helpType_transport', 'typeOfCar']
class TranslationFilter(django_filters.FilterSet):
    class Meta:
        model = TranslationOffer
        fields = ['languages' ]