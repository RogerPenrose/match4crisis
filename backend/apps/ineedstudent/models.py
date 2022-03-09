from datetime import datetime
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.mapview.utils import plzs

# Create your models here.
"""A typical class defining a model, derived from the Model class."""


class Hospital(models.Model):

    # Datenbankfeatures
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    COUNTRY_CODE_CHOICES = [
        ("DE", "Deutschland"),
        ("AT", "Österreich"),
    ]
    countrycode = models.CharField(max_length=2, choices=COUNTRY_CODE_CHOICES, default="DE",)

    max_mails_per_day = models.IntegerField(default=settings.MAX_EMAILS_PER_HOSPITAL_PER_DAY)

    # Kontaktdaten
    sonstige_infos = models.TextField(default="", max_length=10000)
    ansprechpartner = models.CharField(max_length=100, default="")
    telefon = models.CharField(max_length=100, default="")
    firmenname = models.CharField(max_length=100, default="")
    plz = models.CharField(max_length=5, null=True)

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    registration_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="approved_by"
    )
    appears_in_map = models.BooleanField(default=False)

    datenschutz_zugestimmt = models.BooleanField(default=False)
    einwilligung_datenweitergabe = models.BooleanField(default=False)

    # Metadata
    class Meta:
        ordering = ["registration_date"]

    # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""  # noqa: D401
        return self.uuid

    def clean(self):
        if self.plz not in plzs[self.countrycode]:
            raise ValidationError(
                _(str(self.plz) + " ist keine Postleitzahl in " + self.countrycode)
            )
