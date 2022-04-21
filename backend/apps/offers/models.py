import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.accounts.models import User, Languages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from match4crisis.constants.countries import countries
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
    ('AC', _('Unterbringung')),
    ('TL', _('Übersetzung')),
    ('TR', _('Logistik')),
    ('BU', _('Bürokratie')),
    ('MP', _('Manneskraft')),
    ('CL', _('Kinderbetreuung Langzeit')),
    ('BA', _('Babysitting')),
    ('WE', _('Medizinische Hilfe')),
    ('JO', _('Jobangebot')),
    ('DO', _('Spende'))
    ]
    offerTitle = models.TextField(max_length=100, default="")
    location = models.TextField(max_length=300, default="")
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    bb = models.CharField(max_length=300, default="")
    offerType = models.CharField(max_length=2, choices=OFFER_CHOICES, default="AC") # Use this to track between "Bus", "Car", "Transporter" ?
    cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    #image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png')
    # TODO maybe this should be Helper instead of User?
    userId = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)# Can be blank for shell testing...
    offerDescription = models.TextField(default="")
    isDigital = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField('date published', default=timezone.now)
    incomplete = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.offerType
class ChildcareOfferLongterm(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    GENDER_CHOICES = [
        ('NO', _("Keine Angabe")),
        ('FE', _("Weiblich")),
        ('MA', _("Männlich")),
        ('OT', _("Andere")),
    ]
    gender_longterm = models.CharField(max_length=2, choices=GENDER_CHOICES, default="NO")
class ChildcareOfferShortterm(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    GENDER_CHOICES = [
        ('NO', _("Keine Angabe")),
        ('FE', _("Weiblich")),
        ('MA', _("Männlich")),
        ('OT', _("Andere")),
    ]
    gender_shortterm = models.CharField(max_length=2, choices=GENDER_CHOICES, default="NO")
    numberOfChildrenToCare =  models.IntegerField(default=2)
    isRegular = models.BooleanField(default=False)
class JobOffer(models.Model):
    JOB_CHOICES = [
        ("ACA",_("Akademische Hilfe,")),
        ("ADM",_("Administration,")),
        ("ADV",_("Fortbildung,")),
        ("CON",_("Konferenzen und Events,")),
        ("FAC",_("Anlagenbetrieb,")),
        ("FIN",_("Finance und Buchhaltung,")),
        ("GEN",_("Allgemeine Verwaltung,")),
        ("HEA",_("Gesundheitsservices,")),
        ("HUM",_("Personalwesen,")),
        ("INF",_("IT,")),
        ("INT",_("International Program and Services,")),
        ("LEG",_("Jura,")),
        ("LIB",_("BÜchereiverwaltung,")),
        ("MAR",_("Marketing,")),
        ("OFF",_("Büro / Verwaltung,")),
        ("PER",_("Kunst und Museumsverwaltung,")),
        ("PUB",_("Öffentliche Sicherheit,")),
        ("RES",_("Forschung und Forschungsadministration,")),
        ("SPO",_("Sport,")),
        ("STU",_("Studentische Dienstleistungen,")),
        ("HAN",_("Handwerk"))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    jobType = models.CharField(max_length=3, choices=JOB_CHOICES, default="ACA")
    jobTitle = models.CharField(max_length=128, blank=True)
    requirements = models.TextField(blank=True)
class DonationOffer(models.Model):
    account= models.CharField(max_length=350)
    donationTitle = models.CharField(max_length=128, blank=True)
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)

class BuerocraticOffer(models.Model):
    HELP_CHOICES= [('AM', _('Begleitung')), ('LE', _('Juristische Hilfe')), ('OT', _('Andere'))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    helpType_buerocratic = models.CharField(max_length=2, choices=HELP_CHOICES, default="AM")
class ImageClass(models.Model):
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png', blank=False)
    offerId = models.ForeignKey(GenericOffer, on_delete=models.PROTECT)
    image_id = models.IntegerField(primary_key=True)
class ManpowerOffer(models.Model):
    HELP_CHOICES= [('ON', _('Online')), ('OS', _('Vor Ort'))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    helpType_manpower = models.CharField(max_length=2, choices=HELP_CHOICES, default="ON")

class AccommodationOffer(models.Model):

    ACCOMMODATIONCHOICES = [
        ('SO', _('Sofa / Bed')),
        ('RO', _('Eigener Raum')),
        ('HO', _('Gesamte Wohnung / Haus'))
    ]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    numberOfAdults = models.IntegerField(default=2)
    numberOfChildren = models.IntegerField(default=0, blank=True)
    numberOfPets = models.IntegerField(default=0, blank=True)
    typeOfResidence = models.CharField(max_length=2, choices=ACCOMMODATIONCHOICES, default="SO" )
    startDateAccommodation = models.DateField(default=timezone.now)
    endDateAccommodation = models.DateField(blank =True, null=True)
    def __str__(self):
        return self.typeOfResidence

class WelfareOffer(models.Model):
    WELFARE_CHOICES = [("ELD", _("Altenpflege")),("DIS", _("Behindertenpflege")), ("PSY", _("Psychologische Hilfe"))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    
    helpType_welfare = models.CharField(max_length=3, choices=WELFARE_CHOICES, default="ELD") # Use this to track between "Bus", "Car", "Transporter" ?

class TransportationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    #country = models.CharField(max_length=200) # Do this as a select ? 
    
    locationEnd = models.TextField(max_length=300)
    latEnd = models.FloatField(null=True)
    lngEnd = models.FloatField(null=True)
    bbEnd =  models.CharField(max_length=300)
    date=models.DateField(default=timezone.now)
    numberOfPassengers = models.IntegerField(default=2)
class TranslationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    
    firstLanguage = models.ForeignKey(Languages,verbose_name=_("Erste Sprache"), related_name='firstLanguage', on_delete=models.CASCADE, default="de")
    secondLanguage = models.ForeignKey(Languages,verbose_name=_("Zweite Sprache"),related_name='secondLanguage', on_delete=models.CASCADE, default="uk")
# TODO when adding new offer types this needs to be updated
OFFER_MODELS = {
    'AC' : AccommodationOffer,
    'TL' : TranslationOffer,
    'TR' : TransportationOffer,
    'BU' : BuerocraticOffer,
    'BA' : ChildcareOfferShortterm,
    'CL' : ChildcareOfferLongterm,
    'WE' : WelfareOffer,
    'MP' : ManpowerOffer,
    'JO' : JobOffer,
    'DO' : DonationOffer,

}

def getSpecificOffers(genericOffers: list):
    """
    Takes a list of generic offers and returns a list of the matching specific offers.
    """    
    specificOffers = []

    for offer in genericOffers:       
        specOff = OFFER_MODELS[offer.offerType].objects.get(genericOffer=offer)
        specificOffers.append(specOff)

    return specificOffers