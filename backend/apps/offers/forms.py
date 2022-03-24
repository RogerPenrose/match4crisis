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
        model = GenericOffer
        fields = ["offerType", "offerDescription", "country", "postCode",  "streetName", "streetNumber", "cost", "isDigital", "active"]

class ImageForm(forms.Form):
    
    image = forms.ImageField()
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
    typeOfCar = forms.ChoiceField(label=CARTYPE,  choices=CAR_CHOICES ) # Use this to track between "Bus", "Car", "Transporter" ?
    numberOfPassengers = forms.IntegerField(label=PASSENGER_COUNT )
    postCodeEnd = forms.CharField(label=POSTCODE_END, max_length=5, validators=[validate_plz])
    streetNameEnd = forms.CharField(label=STREETNAME_END, max_length=200, required=False)
    streetNumberEnd = forms.CharField(label=STREETNUMBER_END, max_length=4, required=False)
class TranslationForm(forms.Form):
# Translation Fields
    firstLanguage = forms.CharField(label=FIRSTLANGUAGE, max_length=50)
    secondLanguage = forms.CharField(label=SECONDLANGUAGE, max_length=50)

class AccomodationForm(forms.Form):
    # Accomodation Fields
    stayLength = forms.IntegerField(label=STAYLENGTH,localize=False, min_value=0)
    numberOfInhabitants = forms.IntegerField(label=INHABITANTS, localize=False, min_value=1)
    petsAllowed = forms.BooleanField(label=PETS_ALLOWED,initial=False, required=False)
