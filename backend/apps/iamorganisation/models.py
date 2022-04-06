from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from match4crisis.constants.countries import countries
from apps.accounts.models import User

class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    organisationName = models.CharField(max_length=300, default="", verbose_name=_("Name der Organisation"))
    contactPerson = models.CharField(max_length=100, default="", verbose_name=_("Kontaktperson"))
    # Phone number is already stored in User Table
    clubNumber = models.CharField(max_length=20, verbose_name=_("Vereinsnummer")) # Vereinsnummer
    country = models.CharField(max_length=50, choices=countries)
    postalCode = models.CharField(max_length=15)
    streetNameAndNumber = models.CharField(max_length=50)
    
    generalInfo = models.TextField(max_length=10000, default="", blank=True, verbose_name=_("Allgemeine Information"))

    isApproved = models.BooleanField(default=False, verbose_name=_("Ist approved"))
    approvalDate = models.DateTimeField(null=True, verbose_name=_("Approval-Datum"))
    approvedBy = models.ForeignKey(
        User, on_delete=models.SET_NULL, db_constraint=False, null=True, related_name="approvedBy", verbose_name=_("Approved von")
    )
    appearsInMap = models.BooleanField(default=False)

    acceptedPrivacyStatement = models.BooleanField(default=False, verbose_name=_("Datenschutzerklärung akzeptiert")) # Datenschutzerklärung
    acceptedDataSharing = models.BooleanField(default=False, verbose_name=_("Datenweitergabeerklärung akzeptiert")) # Datenweitergabe

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

    @property
    def address(self):
        return '{0}, {1}, {2}'.format(self.streetNameAndNumber, self.postalCode, self.country)

    def __str__(self):
        return self.organisationName

class HelpRequest(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=False, related_name="requests")
    radius = models.IntegerField(default=5)
    title = models.CharField(max_length=256, default="")
    description = models.TextField(max_length=100000, default="")
    recipientCount = models.IntegerField(default=0)