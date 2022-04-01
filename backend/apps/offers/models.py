from datetime import datetime
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.accounts.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.iofferhelp.models import Helper
def validate_plz(value):
    try:
        number = int(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid postcode'),
            params={'value': value},
        )

class GenericOffer(models.Model):

    OFFER_CHOICES = [
    ('AC', 'Accomodation'),
    ('TL', 'Translation'),
    ('TR', 'Transportation'),
    ('AP', 'Accompaniment')
    ]


    offerType = models.CharField(max_length=2, choices=OFFER_CHOICES, default="AC") # Use this to track between "Bus", "Car", "Transporter" ?
    postCode = models.CharField(max_length=5, validators=[validate_plz])
    streetName = models.CharField(max_length=200,blank=True)
    streetNumber = models.CharField(max_length=10,blank=True)#Edge case of number+Letter forces us to use a character field here...
    cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    #image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png')
    country = models.CharField(max_length=200) # Do this as a select ? 
    # TODO maybe this should be Helper instead of User?
    userId = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)# Can be blank for shell testing...
    offerDescription = models.TextField()
    isDigital = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField('date published', default=timezone.now())
    incomplete = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.offerType

class AccompanimentOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
class ImageClass(models.Model):
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png', blank=False)
    offerId = models.ForeignKey(GenericOffer, on_delete=models.PROTECT)
    image_id = models.IntegerField(primary_key=True)
ACCOMODATIONCHOICES = {
    ('SO', 'Sofa / Bed'),
    ('RO', 'Private Room'),
    ('HO', 'Whole Flat / House')
}
class AccomodationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    numberOfAdults = models.IntegerField(default=2)
    numberOfChildren = models.IntegerField(default=2)
    numberOfPets = models.IntegerField(default=2)
    typeOfResidence = models.CharField(ACCOMODATIONCHOICES,max_length=2, default="SO" )
    streetName = models.CharField(max_length=200, blank=True)
    streetNumber = models.CharField(max_length=4, blank=True)#Edge case of number+Letter forces us to use a character field here...
    stayLength = models.IntegerField(default=14, blank=True) # Check : https://docs.djangoproject.com/en/4.0/ref/models/fields/#:~:text=of%20decimal%20fields.-,DurationField,-%C2%B6


class TransportationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=200) # Do this as a select ? 
    
    postCodeEnd = models.CharField(max_length=5, validators=[validate_plz])
    streetNameEnd = models.CharField(max_length=200)
    streetNumberEnd = models.CharField(max_length=4)#Edge case of number+Letter forces us to use a character field here...
 

    CAR_CHOICES = [
    ('LKW', 'Large Truck'),
    ('CAR', 'Car'),
    ('TRA', 'Transporter'),
    ('BUS', 'Bus')
    ]
    typeOfCar = models.CharField(max_length=3, choices=CAR_CHOICES, default="CAR") # Use this to track between "Bus", "Car", "Transporter" ?
    numberOfPassengers = models.IntegerField(default=2)
class TranslationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    firstLanguage = models.CharField(max_length=50)
    secondLanguage = models.CharField(max_length=50)

# TODO when adding new offer types this needs to be updated
OFFER_MODELS = {
    'AC' : AccomodationOffer,
    'TL' : TranslationOffer,
    'TR' : TransportationOffer,
}

def getSpecificOffers(genericOffers: list):
    """
    Takes a list of generic offers and returns a list of the matching specific offers.
    """    
    specificOffers = []

    for offer in genericOffers:       
        specOff = OFFER_MODELS[offer.offerType].objects.get(genericOffer=offer.pk)
        specificOffers.append(specOff)

    return specificOffers