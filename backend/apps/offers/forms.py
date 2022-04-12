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
OFFERTYPE = "Offer Type"
OFFERDESCRIPTION = "Offer Description"
COUNTRY = "Country"
POSTCODE = "Postcode"
STREETNAME = "Streetname"
HOUSENUMBER = "Housenumber"
STREETNAME_END="Streetname (Destination)"
STREETNUMBER_END="Housenumber (Destination)"
POSTCODE_END = "Postcode (Destination)"
PRICE = "Price"
PETS_ALLOWED="Are pets allowed?"
PASSENGER_COUNT="Number of Passengers"
CARTYPE="Type of car"
FIRSTLANGUAGE="Translating from"
SECONDLANGUAGE="Translating to"
STAYLENGTH= "Maximum length of stay (Days)"
INHABITANTS_ADULTS="Maximum number of Adults"
INHABITANTS_CHILDREN="Maximum number of Children"
INHABITANTS_PETS="Maximum number of Pets"
DIGITAL="Digital Offer"
ACTIVE="Active Offer"
RESIDENCE="Type of residence"
HELPTYPE="Type of Buerocratic Aid"
HELPTYPE_MP="Type of Manpower"
GENDER="Gender"
REGULAR_CHILDCARE="Regular Childcare"
AMOUNT_OF_CHILDREN="How many Children"
JOBTYPE="Type of Job"
JOBREQS = "Requirements"
JOBTITLE= "Jobtitle"
HELPTYPE_WE="Type of Medical Assistance"
BANKACCOUNT="Bank Data"
STARTDATE= "Starting"
ENDDATE = "Ending"
DONATION_TITLE="Title"
DEPARTUREDATE="Date"
NUMBERADULTS="How many Adults"
NUMBERPETS = "How many Pets"
IMAGE = "Upload Image"
LOCATION="Location"
logger = logging.getLogger("django")
class GenericForm(forms.ModelForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = GenericOffer

        fields = ["offerType", "offerDescription","location", "lat","lng", "bb", "cost", "isDigital", "active"]
        labels={
            "offerType": OFFERTYPE,
            "offerDescription": OFFERDESCRIPTION, 
            "cost": PRICE, 
            "isDigital": DIGITAL, 
            "location": LOCATION,
            "active": ACTIVE,
        }
        widgets = {
            'location': forms.TextInput(attrs={ 'class': 'form-control'}),
            'lat': forms.TextInput(attrs={'class': 'form-control'}),
            'lng': forms.TextInput(attrs={'class': 'form-control'}),
            'bb': forms.TextInput(attrs={'class': 'form-control'}),
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
    gender = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
class ChildcareFormShortterm(forms.Form):
    gender = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
    isRegular = forms.BooleanField(label=REGULAR_CHILDCARE, widget=forms.CheckboxInput( attrs={'class': 'custom-control-input'}))
    numberOfChildrenToCare = forms.IntegerField(label=AMOUNT_OF_CHILDREN, widget=forms.NumberInput(attrs={'class': 'form-control'}) )

class ImageForm(forms.Form):
    
    image = forms.ImageField(label=IMAGE, widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)
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
    postCodeEnd = forms.CharField(label=POSTCODE_END, max_length=5, validators=[validate_plz], widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNameEnd = forms.CharField(label=STREETNAME_END, max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNumberEnd = forms.CharField(label=STREETNUMBER_END, max_length=4, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
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
   