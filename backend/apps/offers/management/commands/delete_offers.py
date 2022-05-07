"""
Add testing data to database.

route /accounts/add_data aufrufen um user zu generieren
muss in urls.py auskommentiert werden
"""
from django.core.management.base import BaseCommand, no_translations
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import numpy as np
from apps.accounts.models import User
from apps.offers.models import GenericOffer



class Command(BaseCommand):
    help = "Deletes all fake offers." 
   

    
    def handle(self, *args, **options):
       
        if settings.DEBUG:
            all_fake = GenericOffer.objects.filter(offerDescription="Automatically generated")
            count = all_fake.count()
            all_fake.delete()
            return "Done, deleted "+str(count)+" entries." 
        return ("Access forbidden: Not in debug mode.")
