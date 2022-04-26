import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import BaseUserManager

from match4crisis.constants.choices import GENDER_CHOICES

logger = logging.getLogger("django")

# source: https://tech.serhatteker.com/post/2020-01/email-as-username-django/
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)




class Languages(models.Model):
    """ Database containing numerous languages. The ISO 639-1 Code is the Primary Key"""
    isoCode = models.CharField(max_length=2, primary_key=True, verbose_name=_('ISO 639-1 Code'))
    englishName = models.CharField(max_length=128, verbose_name=_('English Name'))
    nativeName = models.CharField(max_length=128, verbose_name=_("Native Name"))
    country = models.CharField(max_length=2, verbose_name=_("Affiliated Country"))

    def __str__(self) -> str:
        return "%s (%s)" % (self.englishName, self.nativeName)


class User(AbstractUser):
    """ A custom User Model serving as a basis for all accounts."""

    # Note: M4H simply used the email address as username, which lead to duplicate entries for every user
    # To avoid this and for simplicity (so we don't have to pass the email address twice every time we create a user)
    # our User model has no username and instead uses the email address as the main form of authentication

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    validatedEmail = models.BooleanField(default=False, verbose_name=_("Email bestätigt"))
    emailValidationDate = models.DateTimeField(blank=True, null=True, verbose_name=_("Email bestätigt am"))
    # m:n to the Languages Table using LanguageKnowledge as intermediary
    spokenLanguages = models.ManyToManyField(Languages, through='LanguageKnowledge', blank=True, verbose_name=_("Sprachkenntnisse"))
    # Regex for Phone Numbers in E164 format
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, null=True, blank=True, verbose_name=_("Telefonnummer"))
    # Should the phone number be visible to contacts
    sharePhoneNumber = models.BooleanField(default=False, verbose_name=_("Telefonnummer teilen"))

    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default="NO")

    isRefugee = models.BooleanField(default=False)
    isHelper = models.BooleanField(default=False)
    isOrganisation = models.BooleanField(default=False)

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

