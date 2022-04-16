from django import forms
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms
import logging
from match4crisis.constants.countries import countries
from .models import GenericOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, WelfareOffer, JobOffer, DonationOffer, AccommodationOffer
from apps.accounts.models import Languages

def validate_plz(value):
    try:
        number = int(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid postcode'),
            params={'value': value},
        )
OFFERTYPE = "Angebotstyp"
OFFERDESCRIPTION = "Beschreibung"
COUNTRY = "Land"
PRICE = "Preis"
PASSENGER_COUNT="Anzahl der freien Plätze"
FIRSTLANGUAGE="Übersetze von"
SECONDLANGUAGE="Übersetze nach"
INHABITANTS_ADULTS="Anzahl der Erwachsenen"
INHABITANTS_CHILDREN="Anzahl der Kinder"
INHABITANTS_PETS="Anzahl der Haustiere"
DIGITAL="Digital verfügbar"
ACTIVE="Aktives Angebot"
RESIDENCE="Art der Unterbringung"
HELPTYPE="Art der Hilfe"
HELPTYPE_MP="Art der Hilfe"
GENDER="Geschlecht"
REGULAR_CHILDCARE="Regelmäßiges Angebot"
AMOUNT_OF_CHILDREN="Anzahl der Kinder"
JOBTYPE="Art des Jobs"
JOBREQS = "Anforderungen"
JOBTITLE= "Jobtitel"
HELPTYPE_WE="Art der medizinischen Hilfe"
BANKACCOUNT="Bankdaten"
STARTDATE= "Startdatum"
ENDDATE = "Endddatum"
DONATION_TITLE="Titel"
DEPARTUREDATE="Abfahrtsdatum"
NUMBERADULTS="Anzahl der Erwachsenen"
NUMBERPETS = "Anzahl der Haustiere"
IMAGE = "Bild hochladen"
OFFERTITLE = "Titel"
LOCATION="Ort"
LOCATIONEND="Ziel"
logger = logging.getLogger("django")
class GenericForm(forms.ModelForm):
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
            'lat': forms.TextInput(attrs={'class': 'form-control'}),
            'lng': forms.TextInput(attrs={'class': 'form-control'}),
            'bb': forms.TextInput(attrs={'class': 'form-control'}),
            'offerTitle': forms.TextInput(attrs={'class': 'form-control'}),
        'offerType':  forms.Select(attrs={'class': 'form-control'}),
        'offerDescription': forms.Textarea(attrs={'class': 'form-control'}),
        'cost': forms.TextInput(attrs={'class': 'form-control'}),
        'isDigital': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        'active': forms.CheckboxInput(attrs={'class': 'custom-control-input'})
        }
class DonationForm(forms.Form):
    account= forms.CharField(label=BANKACCOUNT, max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))  
    donationTitle= forms.CharField(label=DONATION_TITLE,widget=forms.TextInput(attrs={'class': 'form-control'}))  

class ChildcareFormLongterm(forms.Form):
    gender_longterm = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
class ChildcareFormShortterm(forms.Form):
    gender_shortterm = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
    isRegular = forms.BooleanField(label=REGULAR_CHILDCARE, widget=forms.CheckboxInput( attrs={'class': 'custom-control-input'}))
    numberOfChildrenToCare = forms.IntegerField(label=AMOUNT_OF_CHILDREN, widget=forms.NumberInput(attrs={'class': 'form-control'}) )

class ImageForm(forms.Form):
    
    image = forms.ImageField(label=IMAGE, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': 'on'}), required=False)
    image.url = forms.CharField(required=False)
    image_id = forms.IntegerField(widget = forms.HiddenInput(),required=False)

 
class JobForm(forms.Form):
    jobType= forms.CharField(label=JOBTYPE, max_length=3, widget=forms.Select(choices=JobOffer.JOB_CHOICES, attrs={'class': 'form-control'}))  
    jobTitle= forms.CharField(label=JOBTITLE, max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))  
    requirements= forms.CharField(label=JOBREQS,widget=forms.Textarea(attrs={'class': 'form-control'}))  
class ManpowerForm(forms.Form):
    helpType_manpower= forms.CharField(label=HELPTYPE_MP, max_length=2, widget=forms.Select(choices=ManpowerOffer.HELP_CHOICES, attrs={'class': 'form-control'}))
class WelfareForm(forms.Form):
    helpType_welfare= forms.CharField(label=HELPTYPE_WE, max_length=2, widget=forms.Select(choices=WelfareOffer.WELFARE_CHOICES, attrs={'class': 'form-control'}))
      
class BuerocraticForm(forms.Form):
    helpType_buerocratic= forms.CharField(label=HELPTYPE, max_length=2, widget=forms.Select(choices=BuerocraticOffer.HELP_CHOICES, attrs={'class': 'form-control'}))
class TransportationForm(forms.Form):
    date=forms.DateField(label=DEPARTUREDATE,widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    numberOfPassengers = forms.IntegerField(label=PASSENGER_COUNT, widget=forms.NumberInput(attrs={'class': 'form-control'}) )
    locationEnd = forms.CharField( max_length=300, label=LOCATIONEND, widget=forms.TextInput(attrs={'class': 'form-control'}))
    latEnd = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    lngEnd = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bbEnd = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
class TranslationForm(forms.Form):
# Translation Fields
#queryset=Languages.objects.all(), 
    firstLanguage =   forms.ChoiceField(widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))#"englishName__icontains", "nativeName__icontains"]))
    secondLanguage =  forms.ChoiceField( widget=s2forms.ModelSelect2Widget(model=Languages, search_fields=["englishName__icontains", "nativeName__icontains"]))
      
class AccommodationForm(forms.Form):
   
    startDateAccommodation=   forms.DateField(label=STARTDATE, widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    endDateAccommodation=  forms.DateField(label=ENDDATE, widget=forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}))
    numberOfAdults= forms.IntegerField(label=NUMBERADULTS,  widget=forms.NumberInput(attrs={'class':'form-control'}))
    numberOfChildren= forms.IntegerField(label=AMOUNT_OF_CHILDREN, widget=forms.NumberInput(attrs={'class':'form-control'}))
    numberOfPets= forms.IntegerField(label=NUMBERPETS, widget=forms.NumberInput(attrs={'class':'form-control'}))
    typeOfResidence =  forms.CharField(max_length=2, label=RESIDENCE,widget=forms.Select(choices=AccommodationOffer.ACCOMMODATIONCHOICES, attrs={'class':'form-control'}))
   