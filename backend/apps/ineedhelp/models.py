from django.db import models
from django.http import HttpResponse
from django.utils import timezone
import uuid
from apps.accounts.models import User
from apps.offers.models import GenericOffer

class Refugee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

    favouriteOffers = models.ManyToManyField(GenericOffer, related_name="favouritedBy")

    # The maximum number of recently viewed and recently contacted offers to save (for preserving space)
    MAX_RECENTLY_VIEWED = 25
    MAX_RECENTLY_CONTACTED = 25
    recentlyViewedOffers = models.ManyToManyField(GenericOffer, through='RecentlyViewedIntermediary', related_name="recentlyViewedBy")
    recentlyContactedOffers = models.ManyToManyField(GenericOffer, through='RecentlyContactedIntermediary', related_name="recentlyContactedBy")


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

    def addRecentlyViewedOffer(self, offer : GenericOffer):
        """
        Adds an offer to the recently viewed offers and removes the first one if the maximum has been reached.\n
        If the viewed offer already exists changes the date viewed to now.
        """
        try:
            existingEntry = RecentlyViewedIntermediary.objects.get(refugee = self, offer=offer)
            existingEntry.dateViewed = timezone.now()
            existingEntry.save()
        except RecentlyViewedIntermediary.DoesNotExist:
            self.recentlyViewedOffers.add(offer, through_defaults={'dateViewed': timezone.now()})
            if(self.recentlyViewedOffers.all().count() > self.MAX_RECENTLY_VIEWED):
                RecentlyViewedIntermediary.objects.filter(refugee=self).earliest('dateViewed').delete()
    
    def addRecentlyContactedOffer(self, offer : GenericOffer):
        """
        Adds an offer to the recently contacted offers and removes the first one if the maximum has been reached.\n
        If the contacted offer already exists changes the date contacted to now.
        """
        try:
            existingEntry = RecentlyContactedIntermediary.objects.get(refugee = self, offer=offer)
            existingEntry.dateContacted = timezone.now()
            existingEntry.save()
        except RecentlyContactedIntermediary.DoesNotExist:
            self.recentlyContactedOffers.add(offer, through_defaults={'dateContacted': timezone.now()})

            if(self.recentlyContactedOffers.all().count() > self.MAX_RECENTLY_VIEWED):
                RecentlyContactedIntermediary.objects.filter(refugee=self).earliest('dateContacted').delete()


class RecentlyViewedIntermediary(models.Model):
    """
    The intermediary model that is used for the m:n-relation between Refugees and recently viewed GenericOffers.\n
    Additionally stores the date, on which the offer was viewed (for sorting)
    """
    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    offer = models.ForeignKey(GenericOffer, on_delete=models.CASCADE)
    dateViewed = models.DateTimeField(null=False)

class RecentlyContactedIntermediary(models.Model):
    """
    The intermediary model that is used for the m:n-relation between Refugees and recently contacted GenericOffers.\n
    Additionally stores the date, on which the offer was contacted (for sorting)
    """
    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    offer = models.ForeignKey(GenericOffer, on_delete=models.CASCADE)
    dateContacted = models.DateTimeField(null=False)