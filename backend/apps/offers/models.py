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
    ('BU', 'Buerocratic'),
    ('MP', 'Manpower'),
    ('CL', 'Childcare Permanent'),
    ('BA', 'Babysitting'),
    ('WE', 'Medical Assistance')
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
class ChildcareOfferLongterm(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    GENDER_CHOICES = [
        ('NO', "Don't want to disclose"),
        ('FE', "Female"),
        ('MA', "Male"),
    ]
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default="NO")
class ChildcareOfferShortterm(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    GENDER_CHOICES = [
        ('NO', "Don't want to disclose"),
        ('FE', "Female"),
        ('MA', "Male"),
    ]
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default="NO")
    numberOfChildrenToCare =  models.IntegerField(default=2)
    isRegular = models.BooleanField(default=False)
class JobOffer(models.Model):
    JOB_CHOICES = [
        ("Academic Support", "ACA"),
        ("Administration", "ADM"),
        ("Advancement", "ADV"),
        ("Conference and Events","CON"),
        ("Facility Operations", "FAC"),
        ("Finance and Accounting", "FIN"),
        ("General Administration", "GEN"),
        ("Health Services", "HEA"),
        ("Human Resources", "HUM"),
        ("Information Technology", "INF"),
        ("International Program and Services", "INT"),
        ("Legal", "LEG"),
        ("Library Administration", "LIB"),
        ("Marketing, Communication and External Affairs", "MAR"),
        ("Office and Admin Support", "OFF"),
        ("Performing Arts and Museum Administration", "PER"),
        ("Public Safety", "PUB"),
        ("Research and Program Admin", "RES"),
        ("Sports and Recreation", "SPO"),
        ("Student Services", "STU"),
        ("Handicraft profession", "HAN")]

class BuerocraticOffer(models.Model):
    HELP_CHOICES= [('AM', 'Accompaniment'), ('LE', 'Legal'), ('OT', 'Other')]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    helpType = models.CharField(max_length=2, choices=HELP_CHOICES, default="AM")
class ImageClass(models.Model):
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png', blank=False)
    offerId = models.ForeignKey(GenericOffer, on_delete=models.PROTECT)
    image_id = models.IntegerField(primary_key=True)
ACCOMODATIONCHOICES = {
    ('SO', 'Sofa / Bed'),
    ('RO', 'Private Room'),
    ('HO', 'Whole Flat / House')
}
class ManpowerOffer(models.Model):
    HELP_CHOICES= [('ON', 'Online'), ('OS', 'On-site')]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    helpType = models.CharField(max_length=2, choices=HELP_CHOICES, default="ON")

class AccomodationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    numberOfAdults = models.IntegerField(default=2)
    numberOfChildren = models.IntegerField(default=0, blank=True)
    numberOfPets = models.IntegerField(default=0, blank=True)
    typeOfResidence = models.CharField(ACCOMODATIONCHOICES,max_length=2, default="SO" )
    streetName = models.CharField(max_length=200, blank=True)
    streetNumber = models.CharField(max_length=4, blank=True)#Edge case of number+Letter forces us to use a character field here...
    stayLength = models.IntegerField(default=14, blank=True) # Check : https://docs.djangoproject.com/en/4.0/ref/models/fields/#:~:text=of%20decimal%20fields.-,DurationField,-%C2%B6
    def __str__(self):
        return self.typeOfResidence
class WelfareOffer(models.Model):
    WELFARE_CHOICES = [("ELD", "Elderly Care"),("DIS", "Care for handicapped People"), ("PSY", "Psychological Aid")]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    
    helpType = models.CharField(max_length=3, choices=WELFARE_CHOICES, default="CAR") # Use this to track between "Bus", "Car", "Transporter" ?

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
    'BU' : BuerocraticOffer,
    'BA' : ChildcareOfferShortterm,
    'CL' : ChildcareOfferLongterm,
    'WE' : WelfareOffer
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