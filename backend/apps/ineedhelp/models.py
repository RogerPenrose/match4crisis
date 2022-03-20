from django.db import models

from backend.apps.accounts.models import User

class Refugee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Which additional information do we need for the refugees?