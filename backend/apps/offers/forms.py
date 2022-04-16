from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
import logging
from match4crisis.constants.countries import countries
from .models import GenericOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, TranslationOffer, TransportationOffer, WelfareOffer, JobOffer, DonationOffer, AccommodationOffer
from apps.accounts.models import Languages

def validate_plz(value):
    try:
        number = int(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid postcode'),
            params={'value': value},
        )
OFFERTYPE = _("Angebotstyp")
OFFERDESCRIPTION = _("Beschreibung")
COUNTRY = _("Land")
PRICE = _("Preis")
PASSENGER_COUNT=_("Anzahl der freien Plätze")
FIRSTLANGUAGE=_("Übersetze von")
SECONDLANGUAGE=_("Übersetze nach")
INHABITANTS_ADULTS=_("Anzahl der Erwachsenen")
INHABITANTS_CHILDREN=_("Anzahl der Kinder")
INHABITANTS_PETS=_("Anzahl der Haustiere")
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
DONATION_TITLE=_("Titel")
DEPARTUREDATE=_("Abfahrtsdatum")
NUMBERADULTS=_("Anzahl der Erwachsenen")
NUMBERPETS = _("Anzahl der Haustiere")
IMAGE = _("Bild hochladen")
OFFERTITLE = _("Titel")
LOCATION=_("Ort")
LOCATIONEND=_("Ziel")
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

        fields = ["offerType", "offerTitle", "offerDescription","location", "lat","lng", "bb", "cost", "isDigital", "active"]
        labels={
            "offerType": OFFERTYPE,
            "offerDescription": OFFERDESCRIPTION, 
            "cost": PRICE, 
            "isDigital": DIGITAL, 
            "location": LOCATION,
            "active": ACTIVE,
            "offerTitle": OFFERTITLE
        }

        widgets = {
            'location': forms.TextInput(attrs={ 'class': 'form-control'}),
        }

class DonationForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = DonationOffer
        exclude = ("genericOffer",)

        labels = {
            "account" : BANKACCOUNT,
            "donationTitle" : DONATION_TITLE,
        }

class ChildcareFormLongterm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ChildcareOfferLongterm
        exclude = ("genericOffer",)

        labels = {
            "gender_longterm" : GENDER,
        }
    
class ChildcareFormShortterm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ChildcareOfferShortterm
        exclude = ("genericOffer",)

        labels = {
            "gender_shortterm" : GENDER,
            "numberOfChildrenToCare" : AMOUNT_OF_CHILDREN,
            "isRegular" : REGULAR_CHILDCARE,
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

class ManpowerForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ManpowerOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType_manpower" : HELPTYPE_MP,
        }

class WelfareForm(forms.Form):
    class Meta:
        attrs = { "class": "form-control"}
        model = WelfareOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType_welfare" : HELPTYPE_WE,
        }
      
class BuerocraticForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = BuerocraticOffer
        exclude = ("genericOffer",)

        labels = {
            "helpType_buerocratic" : HELPTYPE,
        }

class TransportationForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TransportationOffer
        exclude = ("genericOffer",)

        labels = {
            "date" : DEPARTUREDATE,
            "numberOfPassengers" : PASSENGER_COUNT,
            "locationEnd" : LOCATIONEND,
        }

class TranslationForm(forms.ModelForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TranslationOffer
        exclude = ("genericOffer",)

        labels = {
            "firstLanguage" : FIRSTLANGUAGE,
            "secondLanguage" : SECONDLANGUAGE,
        }

        widgets = {
            "firstLanguage" : s2forms.Select2Widget(),
            "secondLanguage" : s2forms.Select2Widget(),
        }
# Translation Fields
#queryset=Languages.objects.all(), 
    #firstLanguage =   forms.ChoiceField(widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))#"englishName__icontains", "nativeName__icontains"]))
    #secondLanguage =  forms.ChoiceField( widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))
      
class AccommodationForm(OfferForm):

    class Meta:
        attrs = { "class": "form-control"}
        model = TranslationOffer
        exclude = ("genericOffer",)

        labels = {
            "startDateAccommodation" : STARTDATE,
            "endDateAccommodation" : ENDDATE,
            "numberOfAdults" : NUMBERADULTS,
            "numberOfChildren" : AMOUNT_OF_CHILDREN,
            "numberOfPets" : NUMBERPETS,
            "typeOfResidence" : RESIDENCE,
        }

      
# TODO when adding new offer types this needs to be updated
OFFER_FORMS = {
    'AC' : AccommodationForm,
    'TL' : TranslationForm,
    'TR' : TransportationForm,
    'BU' : BuerocraticForm,
    'BA' : ChildcareFormShortterm,
    'CL' : ChildcareFormLongterm,
    'WE' : WelfareForm,
    'MP' : ManpowerForm,
    'JO' : JobForm,
    'DO' : DonationForm,

}