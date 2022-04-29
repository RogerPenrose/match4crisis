from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import uuid

from localflavor.generic.models import IBANField

from match4crisis.constants.countries import countries
from apps.accounts.models import User

class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    organisationName = models.CharField(max_length=300, default="", verbose_name=_("Name der Organisation"))
    contactPerson = models.CharField(max_length=100, default="", verbose_name=_("Kontaktperson"))
    # Phone number is already stored in User Table
    country = models.CharField(max_length=50, choices=countries)
    postalCode = models.CharField(max_length=15)
    city = models.CharField(max_length=128, default="")
    streetNameAndNumber = models.CharField(max_length=50)

    about = models.TextField(max_length=500000, verbose_name=_("Über uns"), default="")
    logo = models.ImageField(upload_to="organisation_logos/", null = True, blank=True)
    
    isApproved = models.BooleanField(default=False)
    approvalDate = models.DateTimeField(null=True)
    approvedBy = models.ForeignKey(
        User, on_delete=models.SET_NULL, db_constraint=False, null=True, related_name="approvedBy", verbose_name=_("Approved von")
    )

    acceptedPrivacyStatement = models.BooleanField(default=False, verbose_name=_("Datenschutzerklärung akzeptiert")) # Datenschutzerklärung
    acceptedDataSharing = models.BooleanField(default=False, verbose_name=_("Datenweitergabeerklärung akzeptiert")) # Datenweitergabe

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

    @property
    def address(self):
        return '{0}, {1} {2}, {3}'.format(self.streetNameAndNumber, self.postalCode, self.city, self.get_country_display())

    def __str__(self):
        return self.organisationName

class Request(models.Model):
    # The maximum number of images a request can have attached
    MAX_IMAGES = 10
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=False, related_name="requests")
    title = models.CharField(max_length=256, default="")
    description = models.TextField(max_length=100000, default="")
    createdAt = models.DateTimeField(verbose_name=_("Erstellt am"), default=timezone.now)

class HelpRequest(Request):
    radius = models.IntegerField(default=5)
    recipientCount = models.IntegerField(default=0)
    location = models.CharField(max_length=1000, default="")
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    bb = models.CharField(max_length=300, default="")

class DonationRequest(Request):
    beneficiary = models.CharField(max_length=70, verbose_name=_("Begünstigte/r"))
    iban = IBANField(verbose_name=_("IBAN"))
    reason = models.CharField(max_length=140, verbose_name=_("Spendenstichwort"))

    @property
    def isMaterial(self):
        return False

class MaterialDonationRequest(Request):
    donationType = models.CharField(max_length=500, default="")
    location = models.CharField(max_length=1000, default="")
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    bb = models.CharField(max_length=300, default="")

    @property
    def isMaterial(self):
        return True

class Image(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='requests/%Y/%m/%d/', blank=False)
