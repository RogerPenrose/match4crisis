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
from apps.accounts.models import User, Languages
from apps.offers.models import GenericOffer, AccommodationOffer, TransportationOffer, TranslationOffer, BuerocraticOffer, ManpowerOffer,ChildcareOfferShortterm, ChildcareOfferLongterm, WelfareOffer, JobOffer, DonationOffer



class Command(BaseCommand):
    help = "Populates the database with fake offers." 
    mail = lambda x: "%s@email.com" % x  # noqa: E731
   
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument('n', type=int)
        parser.add_argument('--user_id', help="provide a user_id to be the author of all Offers, else the first available ID will be used", type=int)

    
    def handle(self, *args, **options):
        
        JOB_CHOICES = ["ACA","ADM","ADV","CON","FAC","FIN","GEN","HEA", "HUM","INF","INT","LEG","LIB","MAR","OFF","PER","PUB","RES", "SPO", "STU","HAN"]
        residenceChoices = ['SO','RO', 'HO', 'LE'] 
        HELP_CHOICES_MP= ['ON',  'OS']
        GENDER_CHOICES = ['FE', 'MA', 'NO', 'OT']
        HELP_CHOICES= ['AM', 'LE', 'OT']
        WELFARE_CHOICES = ["ELD", "DIS", "PSY"]
        if options['user_id']:
            user_id = int(options["user_id"])
            user = User.objects.get(id=user_id)
        else:
            user = User.objects.all()[0] 
        if settings.DEBUG:
            n_offers = options["n"]
            counter = 0
            for i in range(n_offers):
                lat = 48 + 6*np.random.random()
                lng = 6 + 9*np.random.random()
                bbStart = {"east": lat+0.09, "west": lat-0.09, "south":lng-0.09, "north": lng+0.09 }
                    
                g = GenericOffer(
                    userId=user, \
                    created_at=timezone.now(), \
                    offerDescription="Automatically generated", \
                    isDigital=False,  \
                    bb = str(bbStart), \
                    lat = lat, \
                    lng = lng, \
                    cost=0.00, \
                    active= (np.random.random() < 0.7), \
                    incomplete= (np.random.random() > 0.7),
                )
                
                if counter == 0: # Accommodation:

                    g.offerType = "AC"
                    g.save()
                    stayLength= np.random.randint(1, 365)
                    a = AccommodationOffer(genericOffer=g, \
                        numberOfAdults=np.random.randint(1, 15), \
                        numberOfChildren=np.random.randint(1, 3), \
                        numberOfPets=np.random.randint(0, 2), \
                        endDateAccommodation=timezone.now() + timedelta(days=stayLength) , \
                        typeOfResidence= residenceChoices[np.random.randint(0,len(residenceChoices)-1)] )     
                    a.save()
                if counter == 1: #Translation

                    g.offerType = "TL"
                    g.save()
                    n = np.random.randint(0, Languages.objects.all().count())
                    m = np.random.randint(0, Languages.objects.all().count())
                    t = TranslationOffer(genericOffer=g, \
                                firstLanguage=Languages.objects.all()[n], \
                                secondLanguage=Languages.objects.all()[m])
                    t.save()
                if counter == 2: # Accompaniment
                    g.offerType = "BU"
                    g.save()
                    b = BuerocraticOffer(genericOffer=g, helpType_buerocratic=HELP_CHOICES[np.random.randint(0,len(HELP_CHOICES)-1)])
                    b.save()
                if counter == 3: # Transportation
                    latEnd = 48 + 6*np.random.random()
                    lngEnd = 6 + 9*np.random.random()
                    bb = {"east": latEnd+0.09, "west": latEnd-0.09, "south":lngEnd-0.09, "north": lngEnd+0.09 }
                    g.offerType = "TR"
                    g.save()
                    t = TransportationOffer(genericOffer=g, \
                        bbEnd = str(bb),\
                        latEnd = latEnd, \
                        lngEnd = lngEnd, \
                        numberOfPassengers=np.random.randint(0, 10))
                    t.save()
                if counter == 4: # Transportation

                    g.offerType = "MP"
                    g.save()
                    b = ManpowerOffer(genericOffer=g, helpType_manpower=HELP_CHOICES_MP[np.random.randint(0,len(HELP_CHOICES_MP)-1)])
                    b.save()
                if counter == 5: # Transportation
                    g.offerType = "CL"
                    g.save()
                    b = ChildcareOfferLongterm(genericOffer=g, gender_longterm=GENDER_CHOICES[np.random.randint(0,len(GENDER_CHOICES)-1)])
                    b.save()
                if counter == 6: # Transportation
                    g.offerType = "BA"
                    g.save()
                    b = ChildcareOfferShortterm(genericOffer=g, isRegular=(np.random.random() < 0.7),numberOfChildrenToCare=np.random.randint(0,5),gender_shortterm=GENDER_CHOICES[np.random.randint(0,len(GENDER_CHOICES)-1)])
                    b.save()
                if counter == 7: # Transportation
                    g.offerType = "WE"
                    g.save()
                    b = WelfareOffer(genericOffer=g, helpType_welfare=WELFARE_CHOICES[np.random.randint(0,len(WELFARE_CHOICES)-1)])
                    b.save()
                if counter == 8: # Transportation
                    g.offerType = "JO"
                    g.save()
                    b = JobOffer(genericOffer=g, jobTitle="Master of awesome.", requirements="10 Year Job experience.", jobType=JOB_CHOICES[np.random.randint(0,len(JOB_CHOICES)-1)])
                    b.save()
                if counter == 9: # Transportation
                    g.offerType = "DO"
                    g.save()
                    b = DonationOffer(genericOffer=g, donationTitle="Human Fund", account="Deutsche Bank DE 12 3456 7891 07893.")
                    b.save()
                    counter = -1
                counter = counter + 1   
            return "Done. "+str(GenericOffer.objects.all().count())+" entries." 
        return ("Access forbidden: Not in debug mode.")
