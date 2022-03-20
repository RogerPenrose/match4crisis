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

#Neue Datenbank