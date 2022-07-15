import logging
import traceback
from django.db import models
from apps.accounts.models import User
from apps.accounts.models import Languages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("django")

class GenericOffer(models.Model):
    OFFER_CHOICES = [
    ('AC', _('Unterbringung')),
    ('TL', _('Übersetzung')),
    ('TR', _('Logistik')),
    ('BU', _('Bürokratie')),
    ('MP', _('Hilfe vor Ort')),
    ('CL', _('Kinderbetreuung')),
    ('WE', _('Medizinische Hilfe')),
    ('JO', _('Jobangebot')),
    ]
    offerTitle = models.CharField(_("Titel"), max_length=100, default="")
    location = models.TextField(_("Ort"), max_length=300, default="")
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    bb = models.CharField(max_length=300, default="")
    offerType = models.CharField(_("Angebotstyp"), max_length=2, choices=OFFER_CHOICES, default="AC") # Use this to track between "Bus", "Car", "Transporter" ?
    cost = models.DecimalField(_("Preis"), max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    #image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png')
    # TODO maybe this should be Helper instead of User?
    userId = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)# Can be blank for shell testing...
    offerDescription = models.TextField(_("Beschreibung"), default="")
    isDigital = models.BooleanField(_("Ist digital"), default=False)
    active = models.BooleanField(_("Ist aktiv"), default=False)
    created_at = models.DateTimeField(_("Erstellt am"), default=timezone.now)
    incomplete = models.BooleanField(_("Ist unvollständig"), default=False)
    requestForHelp = models.BooleanField(_("Ist Hilfsanfrage"), default=False, editable=False)
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
    DISTANCE_CHOICES=[
        ('0', _('5km')),
        ('1', _('10km')),
        ('2', _('20km')), 
        ('3', _('50km')), 
    ]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    isRegular = models.BooleanField(_("Ist regulär"), default=False)
    hasExperience = models.BooleanField(_("Hat Erfahrung"), default=False)
    hasEducation = models.BooleanField(_("Hat Ausbildung"), default=False)
    hasSpace = models.BooleanField(_("Hat Räumlichkeiten"), default=False)
    distance = models.CharField(_("Maximale Entfernung"), max_length=1, choices=DISTANCE_CHOICES, default='0')
    numberOfChildren = models.IntegerField(_("Anzahl Kinder"), default=1, validators=[MinValueValidator(1)])
    helpType_childcare = models.CharField(_("Art der Betreuung"), max_length=2, choices=CHILDCARE_CHOICES, default="GT")
    timeOfDay = models.CharField(_("Tageszeit"), max_length=2, choices=TIME_CHOICES, default="VM")
    
    
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
    jobType = models.CharField(_("Art des Jobs"), max_length=3, choices=JOB_CHOICES, default="ACA")
    jobTitle = models.CharField(_("Jobtitel"), max_length=128, blank=True)
    requirements = models.TextField(_("Anforderungen"), blank=True)

class BuerocraticOffer(models.Model):
    # Don't change this variable name!
    HELP_CHOICES= [('AM', _('Begleitung')), ('LE', _('Juristische Hilfe')), ('OT', _('Andere Bürokratische Hilfe'))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    # Don't change this variable name!
    helpType = models.CharField(_("Art der Hilfe"), max_length=2, choices=HELP_CHOICES, default="AM")

class ImageClass(models.Model):
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default = 'no-img.png', blank=False)
    offerId = models.ForeignKey(GenericOffer, on_delete=models.PROTECT, related_name="images")
    image_id = models.IntegerField(primary_key=True)

class ManpowerOffer(models.Model):
    DISTANCE_CHOICES=[('0', _('0-50km')),('1', _('50-100km')),('2', _('100-200km')), ('3', _('200-400km')), ('4', _('400-600km')), ('5', _('Komplett Flexibel'))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    distanceChoices = models.CharField(_("Einsatzradius"), max_length=1, choices=DISTANCE_CHOICES, default="0")
    canGoforeign = models.BooleanField(_("Auslandseinsatz möglich"), default=False)
    hasExperience_crisis = models.BooleanField(_("Erfahrung mit Krisenmanagement"), default=False)
    hasDriverslicense = models.BooleanField(_("Hat Fahrerlaubnis"), default=False)
    hasMedicalExperience = models.BooleanField(_("Hat medizinische Erfahrung"), default=False)
    describeMedicalExperience = models.TextField(_("Beschreibung medizinische Erfahrung"), default="", blank=True)


class AccommodationOffer(models.Model):

    ACCOMMODATIONCHOICES = [
        ('SO', _('Sofa / Bett')),
        ('RO', _('Eigener Raum')),
        ('HO', _('Gesamte Wohnung / Haus'))
    ]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    numberOfPeople = models.IntegerField(_("Anzahl Personen"), default=2, validators=[MinValueValidator(1)])
    petsAllowed = models.BooleanField(_("Haustiere erlaubt"), default=False, blank=True)
    typeOfResidence = models.CharField(_("Art der Unterkunft"), max_length=2, choices=ACCOMMODATIONCHOICES, default="SO" )
    startDateAccommodation = models.DateField(_("Startdatum der Unterbringung"), default=timezone.now)
    def __str__(self):
        return self.typeOfResidence

class WelfareOffer(models.Model):
    # Don't change this variable name!
    HELP_CHOICES = [("ELD", _("Altenpflege")),("DIS", _("Behindertenpflege")), ("PSY", _("Psychologische Hilfe"))]
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    # Don't change this variable name!
    helpType = models.CharField(_("Art der Hilfe"), max_length=3, choices=HELP_CHOICES, default="ELD") 
    hasEducation_welfare = models.BooleanField(_("Hat Vorerfahrung"), default=False)
    typeOfEducation = models.TextField(_("Beschreibung der Erfahrung"), default="", blank=True)

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
    DISTANCE_CHOICES=[
        ('0', _('0-50km')),
        ('1', _('50-100km')),
        ('2', _('100-200km')), 
        ('3', _('200-400km')), 
        ('4', _('400-600km')), 
        ('5', _('Komplett Flexibel')),
    ]
    # Don't change this variable name!
    helpType = models.CharField(_("Art des Transports"), max_length=2, choices=HELP_CHOICES, default="PT" )
    distance = models.CharField(_("Entfernung (Bereit zu fahren)"), max_length=1, choices=DISTANCE_CHOICES, default='0')
    numberOfPassengers = models.IntegerField(_("Anzahl freier Plätze"), default=2, validators=[MinValueValidator(1)])
    typeOfCar = models.CharField(_("Fahrzeugtyp"), max_length=2, choices=CARCHOICES, default="KW")

class TranslationOffer(models.Model):
    genericOffer = models.OneToOneField(GenericOffer, on_delete=models.CASCADE, primary_key=True)
    languages = models.ManyToManyField(Languages, through='LanguageOfferMap', blank=True, verbose_name=_("Übersetzte Sprachen"))

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

# TODO when adding new offer types this needs to be updated
OFFER_CARD_NAMES = {
    'AC' : 'offers/accommodation-card.html',
    'TL' : 'offers/translation-card.html',
    'TR' : 'offers/transportation-card.html',
    'BU' : 'offers/buerocratic-card.html',
    'CL' : 'offers/childcare-card.html',
    'WE' : 'offers/welfare-card.html',
    'MP' : 'offers/manpower-card.html',
    'JO' : 'offers/job-card.html',
}

def getSpecificOffers(genericOffers: list):
    """
    Takes a list of generic offers and returns a list of the matching specific offers.
    """    
    specificOffers = []

    for offer in genericOffers:
        try:
            specOff = OFFER_MODELS[offer.offerType].objects.get(genericOffer=offer)
            specificOffers.append(specOff)
        except ObjectDoesNotExist:
            logger.error("Specific offer for generic offer with id %s not found: %s" % (offer.pk, traceback.format_exc()))


    return specificOffers