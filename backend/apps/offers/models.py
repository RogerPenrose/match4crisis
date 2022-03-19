from datetime import datetime
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.accounts.models import User
from django.utils.translation import gettext_lazy as _
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
    ('TR', 'Transportation')
    ]
    offerType = models.CharField(max_length=2, choices=OFFER_CHOICES, default="AC") # Use this to track between "Bus", "Car", "Transporter" ?
    
    userId = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)# Can be blank for shell testing...
    offerDescription = models.TextField()
    isDigital = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField('date published')
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.offerType

class AccomodationOffer(models.Model):
    newGenericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=200) # Do this as a select ? 
    postCode = models.CharField(max_length=5, validators=[validate_plz])
    numberOfInhabitants = models.IntegerField()
    petsAllowed = models.BooleanField(default=False)
    streetName = models.CharField(max_length=200, blank=True)
    streetNumber = models.CharField(max_length=4, blank=True)#Edge case of number+Letter forces us to use a character field here...
    stayLength = models.DurationField(blank=True) # Check : https://docs.djangoproject.com/en/4.0/ref/models/fields/#:~:text=of%20decimal%20fields.-,DurationField,-%C2%B6
    cost = models.DecimalField(max_digits=5, decimal_places=2, null=True)


class TransportationOffer(models.Model):
    newGenericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=200) # Do this as a select ? 
    postCodeStart = models.CharField(max_length=5, validators=[validate_plz])
    streetNameStart = models.CharField(max_length=200)
    streetNumberStart = models.CharField(max_length=4)#Edge case of number+Letter forces us to use a character field here...
    
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
    numberOfPassengers = models.IntegerField()
    petsAllowed = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=3, decimal_places=2)

class TranslationOffer(models.Model):
    newGenericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=200) # Do this as a select ? 
    postCode = models.CharField(max_length=5, validators=[validate_plz])
    streetName = models.CharField(max_length=200) # Maybe Skip this?
    streetNumber = models.CharField(max_length=4)
    firstLanguage = models.CharField(max_length=50)
    secondLanguage = models.CharField(max_length=50)