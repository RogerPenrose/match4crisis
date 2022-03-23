from django.db import models
import uuid

from apps.accounts.models import User

class Helper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)


    # One To Many relationship with offers -> Foreign key in Offer model
