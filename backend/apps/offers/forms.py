from django import forms
from django.core.exceptions import ValidationError
import logging
from .models import GenericOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, WelfareOffer, JobOffer, DonnationOffer, AccomodationOffer

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
DONNATION_TITLE="Title"
DEPARTUREDATE="Date"
NUMBERADULTS="How many Adults"
NUMBERPETS = "How many Pets"
logger = logging.getLogger("django")
class GenericForm(forms.ModelForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = GenericOffer

        fields = ["offerType", "offerDescription", "country", "postCode",  "streetName", "streetNumber", "cost", "isDigital", "active"]
        widgets = {
        'offerType':  forms.Select(attrs={'class': 'form-control'}),
        'offerDescription': forms.Textarea(attrs={'class': 'form-control'}),
        'country': forms.TextInput(attrs={'class': 'form-control'}),
        'postCode': forms.TextInput(attrs={'class': 'form-control'}),
        'streetName': forms.TextInput(attrs={'class': 'form-control'}),
        'streetNumber': forms.TextInput(attrs={'class': 'form-control'}),
        'cost': forms.TextInput(attrs={'class': 'form-control'}),
        'isDigital': forms.CheckboxInput(attrs={'class': 'form-control'}),
        'active': forms.CheckboxInput(attrs={'class': 'form-control'})
        }
class DonnationForm(forms.Form):
    account= forms.CharField(label=BANKACCOUNT, max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))  
    donnationTitle= forms.CharField(label=DONNATION_TITLE,widget=forms.TextInput(attrs={'class': 'form-control'}))  

class ChildcareFormLongterm(forms.Form):
    gender = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
class ChildcareFormShortterm(forms.Form):
    gender = forms.CharField(label=GENDER, max_length=2, widget=forms.Select(choices=ChildcareOfferLongterm.GENDER_CHOICES, attrs={'class': 'form-control'}))
    isRegular = forms.BooleanField(label=REGULAR_CHILDCARE, widget=forms.CheckboxInput( attrs={'class': 'form-control'}))
    numberOfChildrenToCare = forms.IntegerField(label=AMOUNT_OF_CHILDREN, widget=forms.NumberInput(attrs={'class': 'form-control'}) )

class ImageForm(forms.Form):
    
    image = forms.ImageField( widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)
    image.url = forms.CharField(required=False)
    image_id = forms.IntegerField(widget = forms.HiddenInput(),required=False)

 
class JobForm(forms.Form):
    jobType= forms.CharField(label=JOBTYPE, max_length=3, widget=forms.Select(choices=JobOffer.JOB_CHOICES, attrs={'class': 'form-control'}))  
    jobTitle= forms.CharField(label=JOBTITLE, max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))  
    requirements= forms.CharField(label=JOBREQS,widget=forms.Textarea(attrs={'class': 'form-control'}))  
class ManpowerForm(forms.Form):
    helpType= forms.CharField(label=HELPTYPE_MP, max_length=2, widget=forms.Select(choices=ManpowerOffer.HELP_CHOICES, attrs={'class': 'form-control'}))
class WelfareForm(forms.Form):
    helpType= forms.CharField(label=HELPTYPE_WE, max_length=2, widget=forms.Select(choices=WelfareOffer.WELFARE_CHOICES, attrs={'class': 'form-control'}))
      
class BuerocraticForm(forms.Form):
    helpType= forms.CharField(label=HELPTYPE, max_length=2, widget=forms.Select(choices=BuerocraticOffer.HELP_CHOICES, attrs={'class': 'form-control'}))
class TransportationForm(forms.Form):
    date=forms.DateField(label=DEPARTUREDATE,widget=forms.DateInput(attrs={'class':'form-control', 'type': 'date'}))
    numberOfPassengers = forms.IntegerField(label=PASSENGER_COUNT, widget=forms.NumberInput(attrs={'class': 'form-control'}) )
    postCodeEnd = forms.CharField(label=POSTCODE_END, max_length=5, validators=[validate_plz], widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNameEnd = forms.CharField(label=STREETNAME_END, max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNumberEnd = forms.CharField(label=STREETNUMBER_END, max_length=4, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
class TranslationForm(forms.Form):
# Translation Fields
    firstLanguage = forms.CharField(label=FIRSTLANGUAGE, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    secondLanguage = forms.CharField(label=SECONDLANGUAGE, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
      
class AccomodationForm(forms.Form):
   
    startDateAccomodation=   forms.DateField(label=STARTDATE, widget=forms.DateInput(attrs={'class':'form-control', 'type': 'date'}))
    endDateAccomodation=  forms.DateField(label=ENDDATE, widget=forms.DateInput(attrs={'class':'form-control', 'type': 'date'}))
    numberOfAdults= forms.IntegerField(label=NUMBERADULTS,  widget=forms.NumberInput(attrs={'class':'form-control'}))
    numberOfChildren= forms.IntegerField(label=AMOUNT_OF_CHILDREN, widget=forms.NumberInput(attrs={'class':'form-control'}))
    numberOfPets= forms.IntegerField(label=NUMBERPETS, widget=forms.NumberInput(attrs={'class':'form-control'}))
    typeOfResidence =  forms.CharField(max_length=2, label=RESIDENCE,widget=forms.Select(choices=AccomodationOffer.ACCOMODATIONCHOICES, attrs={'class':'form-control'}))
   