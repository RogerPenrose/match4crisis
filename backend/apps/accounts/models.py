from datetime import datetime
import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator


from .email_utils import send_mass_mail_sendgrid

logger = logging.getLogger("django")


class Languages(models.Model):
    """ Database containing numerous languages. The ISO 639-1 Code is the Primary Key"""
    isoCode = models.CharField(max_length=2, primary_key=True)
    englishName = models.CharField(max_length=128)
    nativeName = models.CharField(max_length=128)


class User(AbstractUser):
    """ A custom User Model serving as a basis for all accounts."""

    # Note: At the moment there is a username field that is required upon account creation.
    # In M4H this was always set to the E-Mail address

    validatedEmail = models.BooleanField(default=False)
    emailValidationDate = models.DateTimeField(blank=True, null=True)
    # m:n to the Languages Table using LanguageKnowledge as intermediary
    spokenLanguages = models.ManyToManyField(Languages, through='LanguageKnowledge')
    # Regex for Phone Numbers in E164 format
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, null=True)
    # Should the phone number be visible to contacts
    sharePhoneNumber = models.BooleanField(default=False)

    isRefugee = models.BooleanField(default=False)
    isHelper = models.BooleanField(default=False)
    isOrganisation = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email"]

class LanguageKnowledge(models.Model):
    """ The intermediary model that is used for the m:n-relation between User and Languages.\n
    Stores additional information on a user's language knowledge, e.g. the Level"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    # The language level (A1[1]-C2[6])
    level = models.IntegerField(
        default=6,
        validators=[MaxValueValidator(6), MinValueValidator(1)]
    )



"""
ONLY_VALIDATED = 0
ONLY_NOT_VALIDATED = 1
ALL = 2
VALIDATED_AND_APPROVED = 3

VALIDATION_CHOICES = (
    (ONLY_VALIDATED, _("validierte")),
    (ONLY_NOT_VALIDATED, _("nicht validierte")),
    (ALL, _("validierte und nicht validierte")),
    (VALIDATED_AND_APPROVED, _("validiert und von uns approved")),
)
"""

