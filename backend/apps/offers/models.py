import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.accounts.models import User
from apps.accounts.models import Languages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from match4crisis.constants.choices import GENDER_CHOICES
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
    ('CL', _('Kinderbetreuung')),
    ('WE', _('Medizinische Hilfe')),
    ('JO', _('Jobangebot')),
    ]
    offerTitle = models.TextField(max_length=100, default=" ")
    location = models.TextField(max_length=300, default=" ")
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    bb = models.CharField(max_length=300, default=" ")
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
    requestForHelp = models.BooleanField(default=False, editable=False)
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.offerType


class ChildcareOffer(models.Model):
    CHILDCARE_CHOICES = [
        ('GT', _('Ganztagsbetreuung')),
        ('HT', _('Halbtagsbetreuung')),
        ('WE', _('Wochendendsbetreuung'))
    ]
    TIME_CHOICES = [
        ('VM', _('Vormittags')),
        ('NM', _('Nachmittags')),
        ('AB', _('Abends'))
    ]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    isRegular = models.BooleanField(default=False)
    hasExperience = models.BooleanField(default=False)
    hasEducation = models.BooleanField(default=False)
    hasSpace = models.BooleanField(default=False)
    distance = models.IntegerField(default=5)
    numberOfChildren = models.IntegerField(default=1)
    helpType_childcare = models.CharField(max_length=2, choices=CHILDCARE_CHOICES, default="GT")
    timeOfDay = models.CharField(max_length=2, choices=TIME_CHOICES, default="VM")
    
    
class JobOffer(models.Model):
    JOB_CHOICES = [
        ("ACA",_("Akademische Hilfe")),
        ("ADM",_("Administration")),
        ("ADV",_("Fortbildung")),
        ("CON",_("Konferenzen und Events")),
        ("FAC",_("Anlagenbetrieb")),
        ("FIN",_("Finance und Buchhaltung")),
        ("GEN",_("Allgemeine Verwaltung")),
        ("HEA",_("Gesundheitsservices")),
        ("HUM",_("Personalwesen")),
        ("INF",_("IT")),
        ("INT",_("International Program and Services")),
        ("LEG",_("Jura")),
        ("LIB",_("BÜchereiverwaltung")),
        ("MAR",_("Marketing")),
        ("OFF",_("Büro / Verwaltung")),
        ("PER",_("Kunst und Museumsverwaltung")),
        ("PUB",_("Öffentliche Sicherheit")),
        ("RES",_("Forschung und Forschungsadministration")),
        ("SPO",_("Sport")),
        ("STU",_("Studentische Dienstleistungen")),
        ("HAN",_("Handwerk"))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    jobType = models.CharField(max_length=3, choices=JOB_CHOICES, default="ACA")
    jobTitle = models.CharField(max_length=128, blank=True)
    requirements = models.TextField(blank=True)

class BuerocraticOffer(models.Model):
    # Don't change this variable name!
    HELP_CHOICES= [('AM', _('Begleitung')), ('LE', _('Juristische Hilfe')), ('OT', _('Andere Bürokratische Hilfe'))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    helpType = models.CharField(max_length=2, choices=HELP_CHOICES, default="AM")

class ImageClass(models.Model):
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png', blank=False)
    offerId = models.ForeignKey(GenericOffer, on_delete=models.PROTECT)
    image_id = models.IntegerField(primary_key=True)
class ManpowerOffer(models.Model):
    DISTANCE_CHOICES=[('0', _('0-100km')),('1', _('100-200km')), ('2', _('200-400km')), ('3', _('400-600km')), ('4', 'Komplett Flexibel')]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    distanceChoices = models.CharField(max_length=1, choices=DISTANCE_CHOICES, default="0")
    canGoforeign = models.BooleanField(default=False)
    hasExperience_crisis = models.BooleanField(default=False)
    hasDriverslicense = models.BooleanField(default=False)
    hasMedicalExperience = models.BooleanField(default=False)
    describeMedicalExperience = models.TextField(default=" ", blank=True)


class AccommodationOffer(models.Model):

    ACCOMMODATIONCHOICES = [
        ('SO', _('Sofa / Bed')),
        ('RO', _('Eigener Raum')),
        ('HO', _('Gesamte Wohnung / Haus'))
    ]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    numberOfPeople = models.IntegerField(default=2)
    petsAllowed = models.BooleanField(default=0, blank=True)
    typeOfResidence = models.CharField(max_length=2, choices=ACCOMMODATIONCHOICES, default="SO" )
    startDateAccommodation = models.DateField(default=timezone.now)
    def __str__(self):
        return self.typeOfResidence

class WelfareOffer(models.Model):
    # Don't change this variable name!
    HELP_CHOICES = [("ELD", _("Altenpflege")),("DIS", _("Behindertenpflege")), ("PSY", _("Psychologische Hilfe"))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    
    helpType = models.CharField(max_length=3, choices=HELP_CHOICES, default="ELD") 
    hasEducation_welfare = models.BooleanField(default=False)
    typeOfEducation = models.TextField(default="", blank=True)

class TransportationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    # Don't change this variable name!
    HELP_CHOICES=[
        ('PT', _("Personentransport")),
        ('GT', _("Gütertransport"))
    ]
    CARCHOICES=[
        ('KW', _("Kleinwagen")),
        ('MW', _("Mittelklassewagen")),
        ('KM', _("Kombi")),
        ('SU', _("SUV")),
        ('MI', _("Minivan")),
        ('TR', _("Transporter"))
    ]
    helpType = models.CharField(max_length=2, choices=HELP_CHOICES, default="PT" )
    distance = models.IntegerField(default=100)
    numberOfPassengers = models.IntegerField(default=2)
    typeOfCar = models.CharField(max_length=2, choices=CARCHOICES, default="KW")

class TranslationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    languages = models.ManyToManyField(Languages,through='LanguageOfferMap', blank=True, verbose_name=_("Sprachen"))



class LanguageOfferMap(models.Model):
    offer = models.ForeignKey(TranslationOffer, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)

# TODO when adding new offer types this needs to be updated
OFFER_MODELS = {
    'AC' : AccommodationOffer,
    'TL' : TranslationOffer,
    'TR' : TransportationOffer,
    'BU' : BuerocraticOffer,
    'CL' : ChildcareOffer,
    'WE' : WelfareOffer,
    'MP' : ManpowerOffer,
    'JO' : JobOffer,
}

SPECIAL_CASE_OFFERS = {
    'transportation_people': {
        'offerTypeAbbr': 'TR',
        'helpType': {
            'helpType': 'PT'
        },
        'helpTypeChoiceLabel': TransportationOffer.HELP_CHOICES[0][1]
    },
    'transportation_goods': {
        'offerTypeAbbr': 'TR',
        'helpType': {
            'helpType': 'GT'
        },
        'helpTypeChoiceLabel': TransportationOffer.HELP_CHOICES[1][1]
    },
    'buerocracy_companion': {
        'offerTypeAbbr': 'BU',
        'helpType': {
            'helpType': 'AM'
        },
        'helpTypeChoiceLabel': BuerocraticOffer.HELP_CHOICES[0][1]
    },
    'buerocracy_legal': {
        'offerTypeAbbr': 'BU',
        'helpType': {
            'helpType': 'LE'
        },
        'helpTypeChoiceLabel': BuerocraticOffer.HELP_CHOICES[1][1]
    },
    'buerocracy_other': {
        'offerTypeAbbr': 'BU',
        'helpType': {
            'helpType': 'OT'
        },
        'helpTypeChoiceLabel': BuerocraticOffer.HELP_CHOICES[2][1]
    },
    'welfare_elderly': {
        'offerTypeAbbr': 'WE',
        'helpType': {
            'helpType': 'ELD'
        },
        'helpTypeChoiceLabel': WelfareOffer.HELP_CHOICES[0][1]
    },
    'welfare_disabled': {
        'offerTypeAbbr': 'WE',
        'helpType': {
            'helpType': 'DIS'
        },
        'helpTypeChoiceLabel': WelfareOffer.HELP_CHOICES[1][1]
    },
    'welfare_psych': {
        'offerTypeAbbr': 'WE',
        'helpType': {
            'helpType': 'PSY'
        },
        'helpTypeChoiceLabel': WelfareOffer.HELP_CHOICES[2][1]
    },
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