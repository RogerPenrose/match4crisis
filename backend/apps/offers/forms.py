from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
import logging
from .models import *

OFFERTYPE = _("Angebotstyp")
OFFERDESCRIPTION = _("Beschreibung")
COUNTRY = _("Land")
PRICE = _("Preis")
PASSENGER_COUNT=_("Anzahl der freien Plätze")
FIRSTLANGUAGE=_("Übersetze von")
SECONDLANGUAGE=_("Übersetze nach")
NUMBEROFPEOPLE=_("Maximale Anzahl der Bewohner")
PETSALLOWED=_("Haustiere gestattet?")
DIGITAL=_("Digital verfügbar")
ACTIVE=_("Aktives Angebot")
RESIDENCE=_("Art der Unterbringung")
HELPTYPE=_("Art der Hilfe")
HELPTYPE_MP=_("Art der Hilfe")
GENDER=_("Geschlecht")
REGULAR_CHILDCARE=_("Regelmäßiges Angebot")
AMOUNT_OF_CHILDREN=_("Anzahl der Kinder")
JOBTYPE=_("Art des Jobs")
JOBREQS = _("Anforderungen")
JOBTITLE= _("Jobtitel")
HELPTYPE_WE=_("Art der medizinischen Hilfe")
BANKACCOUNT=_("Bankdaten")
STARTDATE= _("Startdatum")
ENDDATE = _("Endddatum")
DEPARTUREDATE=_("Abfahrtsdatum")
NUMBERADULTS=_("Anzahl der Erwachsenen")
NUMBERPETS = _("Anzahl der Haustiere")
IMAGE = _("Bild hochladen")
OFFERTITLE = _("Titel")
LOCATION=_("Ort")
LOCATIONEND=_("Ziel")
DISTANCE=_("Umkreis")
TRANSPORT_TYPE=_("Art des Transports") 
CAR_TYPE= _("Art des Fahrzeugs")
logger = logging.getLogger("django")


class OfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class GenericForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = GenericOffer

        fields = ["offerType", "offerTitle", "offerDescription","location", "lat","lng", "bb", "cost", "active"]
        labels={
            "offerType": OFFERTYPE,
            "offerDescription": OFFERDESCRIPTION, 
            "cost": PRICE, 
            "location": LOCATION,
            "active": ACTIVE,
            "offerTitle": OFFERTITLE
        }

        widgets = {
            'location': forms.TextInput(attrs={ 'class': 'form-control'}),
        }


class ImageForm(forms.Form):
    
    image = forms.ImageField(label=IMAGE, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': 'on'}), required=False)
    image.url = forms.CharField(required=False)
    image_id = forms.IntegerField(widget = forms.HiddenInput(),required=False)

 
class JobForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = JobOffer
        exclude = ("genericOffer",)

        labels = {
            "jobType" : JOBTYPE,
            "jobTitle" : JOBTITLE,
            "requirements" : JOBREQS,
        }

class ChildcareForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ChildcareOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType_childcare" : _("Betreuungsdauer"),
            "timeOfDay": _("Betreuungszeitraum"),
            "distance": _("Umkreis"),
            "numberOfChildren": _("Anzahl an Kindern"),
            "hasSpace": _("Ich habe Räumlichkeiten"),
            "hasEducation": _("Ich habe eine spezielle Ausbildung"),
            "hasExperience": _("Ich habe Betreuungserfahrung"),
            "isRegular": _("Regelmäßige Betreuung möglich")
        }

class ManpowerForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ManpowerOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType_manpower" : HELPTYPE_MP,
            "distanceChoices" : _("Umkreis des Einsatzortes"),
            "canGoforeign": _("Auslandseinsatz ist denkbar"),
            "hasExperience_crisis": _("Habe Erfahrung im Krisenmanagement"),
            "hasMedicalExperience": _("Habe eine Medizinische Ausbildung"),
            "describeMedicalExperience": _("Meine Medizinische Erfahrung umfasst"),
            "hasDriverslicense": _("Habe einen Führerschein")

        }

class WelfareForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = WelfareOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType" : HELPTYPE_WE,
            "hasEducation_welfare": _("Ich habe Vorerfahrung"),
            "typeOfEducation": _("Ausbildung / Erfahrung")
        }
      
class BuerocraticForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = BuerocraticOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType" : HELPTYPE,
        }

class TransportationForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TransportationOffer
        exclude = ("genericOffer",)

        labels = {
            "numberOfPassengers" : PASSENGER_COUNT,
            "distance" : DISTANCE,
            "helpType": TRANSPORT_TYPE,
            "typeOfCar": CAR_TYPE
        }

        widgets = {
            'locationEnd': forms.TextInput(attrs={ 'class': 'form-control'}),
        }

class TranslationForm(forms.ModelForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TranslationOffer
        exclude = ("genericOffer",)

        labels = {
            "languages" : _("Übersetzte Sprachen")
        }

        widgets = {
            "languages" : s2forms.Select2MultipleWidget()

        }
# Translation Fields
#queryset=Languages.objects.all(), 
    #firstLanguage =   forms.ChoiceField(widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))#"englishName__icontains", "nativeName__icontains"]))
    #secondLanguage =  forms.ChoiceField( widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))
      
class AccommodationForm(OfferForm):

    class Meta:
        attrs = { "class": "form-control"}
        model = AccommodationOffer
        exclude = ("genericOffer",)

        labels = {
            "startDateAccommodation" : STARTDATE,
            "numberOfPeople" : NUMBEROFPEOPLE,
            "petsAllowed": PETSALLOWED,
            "typeOfResidence" : RESIDENCE,
        }

        widgets = {
            "startDateAccommodation" : forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}),
        }

      
# TODO when adding new offer types this needs to be updated
OFFER_FORMS = {
    'AC' : AccommodationForm,
    'TL' : TranslationForm,
    'TR' : TransportationForm,
    'BU' : BuerocraticForm,
    'CL' : ChildcareForm,
    'WE' : WelfareForm,
    'MP' : ManpowerForm,
    'JO' : JobForm,
}