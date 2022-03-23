from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from apps.accounts.models import User

class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    organisationName = models.CharField(max_length=300, default="")
    contactPerson = models.CharField(max_length=100, default="")
    # Phone number is already stored in User Table
    clubNumber = models.CharField(max_length=20, default="0") # Vereinsnummer
    country = models.CharField(max_length=50)
    postalCode = models.CharField(max_length=15)
    streetNameAndNumber = models.CharField(max_length=50)
    
    generalInfo = models.TextField(max_length=10000, default="")

    isApproved = models.BooleanField(default=False)
    approvalDate = models.DateTimeField(null=True)
    approvedBy = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="approvedBy"
    )
    appearsInMap = models.BooleanField(default=False)

    acceptedPrivacyStatement = models.BooleanField(default=False) # Datenschutzerklärung
    acceptedDataSharing = models.BooleanField(default=False) # Datenweitergabe

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)


    def __str__(self):
        return self.organisationName
