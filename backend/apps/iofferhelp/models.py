from django.db import models

from backend.apps.accounts.models import User

class Helper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # One To Many relationship with offers -> Foreign key in Offer model