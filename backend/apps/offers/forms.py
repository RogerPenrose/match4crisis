from django import forms
from django.core.exceptions import ValidationError
def validate_plz(value):
    try:
        number = int(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid postcode'),
            params={'value': value},
        )
class GenericForm(forms.Form):
    #Generic Fields
    OFFER_CHOICES = [
    ('AC', 'Accomodation'),\
    ('TL', 'Translation'),\
    ('TR', 'Transportation')\
    ]
    offerType = forms.ChoiceField(choices = OFFER_CHOICES,widget=forms.Select(attrs={"onChange":'refresh()'}))
    offerDescription = forms.CharField(widget=forms.Textarea)
    country = forms.CharField()
    postCode = forms.CharField(max_length=5, validators=[validate_plz])
    streetName = forms.CharField(max_length=200, required=False)
    streetNumber = forms.CharField(max_length=4, required=False)
    

    
class TransportationForm(forms.Form):
    # Transportation Fields
    CAR_CHOICES = [
    ('LKW', 'Large Truck'),\
    ('CAR', 'Car'),\
    ('TRA', 'Transporter'),\
    ('BUS', 'Bus')\
    ]
    typeOfCar = forms.ChoiceField( choices=CAR_CHOICES, ) # Use this to track between "Bus", "Car", "Transporter" ?
    numberOfPassengers = forms.IntegerField()
    petsAllowed = forms.BooleanField(initial=False, required=False)
    postCodeEnd = forms.CharField(max_length=5, validators=[validate_plz])
    streetNameEnd = forms.CharField(max_length=200, required=False)
    streetNumberEnd = forms.CharField(max_length=4, required=False)
    petsAllowed = forms.BooleanField(initial=False, required=False)
    cost = forms.DecimalField(max_digits=3, decimal_places=2)
class TranslationForm(forms.Form):
# Translation Fields
    firstLanguage = forms.CharField(max_length=50)
    secondLanguage = forms.CharField(max_length=50)

class AccomodationForm(forms.Form):
    # Accomodation Fields
    stayLength = forms.IntegerField(localize=False, min_value=0)
    inhabitants = forms.IntegerField(localize=False, min_value=1)
    cost = forms.DecimalField(max_digits=5, decimal_places=2, min_value= 0.00)
    petsAllowed = forms.BooleanField(initial=False, required=False)
