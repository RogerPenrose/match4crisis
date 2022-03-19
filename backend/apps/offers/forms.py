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

class AccomodationForm(forms.Form):
    OFFER_CHOICES = [
    ('AC', 'Accomodation'),
    ('TL', 'Translation'),
    ('TR', 'Transportation')
    ]
    offerType = forms.ChoiceField(choices = OFFER_CHOICES)
    offerDescription = forms.CharField(widget=forms.Textarea)
    country = forms.CharField()
    petsAllowed = forms.BooleanField(initial=False, required=False)
    postCode = forms.CharField(max_length=5, validators=[validate_plz])
    streetName = forms.CharField(max_length=200, required=False)
    streetNumber = forms.CharField(max_length=4, required=False)
    stayLength = forms.IntegerField(localize=False, min_value=0)
    inhabitants = forms.IntegerField(localize=False, min_value=1)
    cost = forms.DecimalField(max_digits=5, decimal_places=2, min_value= 0.00)
