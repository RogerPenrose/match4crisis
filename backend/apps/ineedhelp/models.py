from django.db import models
import uuid

from apps.accounts.models import User
from apps.offers.models import GenericOffer

class Refugee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

    favouriteOffers = models.ManyToManyField(GenericOffer, related_name="favouritedBy")

    def toggleFavourite(self, offer : GenericOffer):
        """
        Adds an offer to this Refugee's favourites and returns True if it isn't already in the favourites.
        Otherwise removes the offer from the favourites and returns False.
        """

        if offer.favouritedBy.filter(user=self.user).exists():
            self.favouriteOffers.remove(offer)
            return False
        else:
            self.favouriteOffers.add(offer)
            return True