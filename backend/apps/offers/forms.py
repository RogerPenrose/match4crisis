from django import forms
from django.core.exceptions import ValidationError
import logging
from .models import GenericOffer, ImageClass

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
INHABITANTS="Maximum number of inhabitants"
DIGITAL="Digital Offer"
ACTIVE="Active Offer"

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

class ImageForm(forms.Form):
    
    image = forms.ImageField( widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)
    image.url = forms.CharField(required=False)
    image_id = forms.IntegerField(widget = forms.HiddenInput(),required=False)

   
      
   
class TransportationForm(forms.Form):
    # Transportation Fields
    CAR_CHOICES = [
    ('LKW', 'Large Truck'),\
    ('CAR', 'Car'),\
    ('TRA', 'Transporter'),\
    ('BUS', 'Bus')\
    ]
    typeOfCar = forms.ChoiceField(label=CARTYPE,  choices=CAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}) ) # Use this to track between "Bus", "Car", "Transporter" ?
    numberOfPassengers = forms.IntegerField(label=PASSENGER_COUNT, widget=forms.NumberInput(attrs={'class': 'form-control'}) )
    postCodeEnd = forms.CharField(label=POSTCODE_END, max_length=5, validators=[validate_plz], widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNameEnd = forms.CharField(label=STREETNAME_END, max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    streetNumberEnd = forms.CharField(label=STREETNUMBER_END, max_length=4, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
class TranslationForm(forms.Form):
# Translation Fields
    firstLanguage = forms.CharField(label=FIRSTLANGUAGE, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    secondLanguage = forms.CharField(label=SECONDLANGUAGE, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

class AccomodationForm(forms.Form):
    # Accomodation Fields
    stayLength = forms.IntegerField(label=STAYLENGTH,localize=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    numberOfInhabitants = forms.IntegerField(label=INHABITANTS, localize=False, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}) )
    petsAllowed = forms.BooleanField(label=PETS_ALLOWED,initial=False, required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}) )
