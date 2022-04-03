from datetime import datetime
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

USER_CHOICES = [
('HE', 'Helper'),
('RF', 'Refugee'),
('OR', 'Organization')
]

def validate_plz(value):
    try:
        number = int(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid postcode'),
            params={'value': value},
        )

class NewUser(AbstractUser):
    userType = models.CharField(max_length=2, choices=USER_CHOICES, default="HE") 
    validatedEmail = models.BooleanField(default=False)
    emailValidationDate = models.DateTimeField(blank=True, null=True) 
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, null=True, blank=True)
    sharePhoneNumber = models.BooleanField(default=False)
    postCode = forms.CharField(label="PLZ", max_length=5, validators=[validate_plz])
    # @todo: Skills (to limit scope of offers)
    