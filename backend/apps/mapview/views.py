from functools import lru_cache
import time
from django.shortcuts import get_object_or_404,render
import logging
import json
from os.path import dirname, abspath, join
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.gzip import gzip_page

from apps.offers.models import GenericOffer, AccommodationOffer, ManpowerOffer,TransportationOffer, TranslationOffer, WelfareOffer, BuerocraticOffer, JobOffer, ChildcareOfferLongterm, ChildcareOfferShortterm
from apps.mapview.utils import get_plz_data, plzs


logger = logging.getLogger("django")
def getCenterOfCity(city):
    current_location = dirname(abspath(__file__))
    with open(join(current_location,"files/cities_to_center.json"), "r") as read_file:
        mappings = json.load(read_file)
        center = mappings.get(city.capitalize())
        if center is not None:
            return center
        else:
            logger.error("NO CENTER FOUND FOR CITY "+city+" Trying for a partial match...")
            for entry in mappings:
                if city.lower() in entry.lower():
                    logger.error("Found a match: "+entry)
                    center = mappings.get(entry)
                    return center
def mapviewjs(request):
    accommodationCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="AC").count()
    transportationCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="TR").count()
    buerocraticCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="BU").count()
    jobCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="JO").count()
    medicalCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="WE").count()
    translationCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="TL").count()
    manpowerCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="TL").count()
    childcareCount = GenericOffer.objects.filter(Q(offerType = "CL")|Q(offerType="BA"),active= True, isDigital = False ).count()
    context = { "entryCount": {"buerocratic": buerocraticCount,"manpower": manpowerCount,
        "accommodation": accommodationCount, "transportation": transportationCount, "translation": translationCount, "childcare": childcareCount, "medical": medicalCount, "job": jobCount 
    },"accommodation" :request.GET.get("accommodation") == 'True', "transportation": request.GET.get("transportation") == 'True',  "translation": request.GET.get("translation")  == 'True',  "generic": request.GET.get("generic")  == 'True'}
    logger.warning("rendering mapview JS ? "+str(request.GET))
    return render(request, 'mapview/mapview.js', context , content_type='text/javascript')
logger = logging.getLogger("django")
# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    startPosition =  [51.13, 10.018]
    zoom = 6
    logger.warning("Received Request in Mapview: "+str(request.GET))
    if request.GET.get("city"):
        startPosition = getCenterOfCity(request.GET.get("city"))
        zoom = 10
        logger.warning("Received: "+str(startPosition))
    context = {
    "startPosition":  startPosition,
    "zoom": zoom,
    "mapbox_token": settings.MAPBOX_TOKEN,
    "transportation": request.GET.get("transportation", "False"),  
    "accommodation" : request.GET.get("accommodation", "False"),
    "manpower" : request.GET.get("manpower", "False"),
    "medical": request.GET.get("medical", "False"), 
    "buerocratic": request.GET.get("buerocratic", "False"),   
    "childcare": request.GET.get("childcare", "False"),  
    "job": request.GET.get("job", "False"),  
    "translation": request.GET.get("translation", "False"),  
    "generic": request.GET.get("generic", "False")
    }
    return render(request, "mapview/map.html", context )

def accommodationOffersJSON(request):
    offers = AccommodationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "numberOfAdults": e.numberOfAdults,
        "numberOfChildren": e.numberOfChildren,
        "numberOfPets": e.numberOfPets,
        "type": e.get_typeOfResidence_display(),
        "startDate": str(e.startDateAccommodation),
        "endDate": str(e.endDateAccommodation),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location,
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) # safe=False is needed to return Arrays
    
def transportationOffersJSON(request):
    offers = TransportationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "destination": e.locationEnd or "N/A",
        "passengers": e.numberOfPassengers,
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 
 
def medicalOffersJSON(request):
    offers = WelfareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_welfare_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 
 
def buerocraticOffersJSON(request):
    offers = BuerocraticOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_buerocratic_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 


def childcareOffersJSON(request):
    offers = ChildcareOfferLongterm.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    shorttermPeriodicOffers = ChildcareOfferShortterm.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, isRegular = True)
    shorttermOnceOffers = ChildcareOfferShortterm.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, isRegular = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "type": "Langzeit",
        "lng": e.genericOffer.lng,
        "children": 1,
        "location": e.genericOffer.location or "N/A",
        "gender": e.get_gender_longterm_display(),
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    for e in shorttermPeriodicOffers:
        facilities.append(
            {
            "lat": e.genericOffer.lat,
            "type": "Kurzzeit (wiederkehrend)",
            "lng": e.genericOffer.lng,
            "children": e.numberOfChildrenToCare,
            "location": e.genericOffer.location or "N/A",
            "gender": e.get_gender_shortterm_display(),
            "bb": e.genericOffer.bb,
            "offerDescription": e.genericOffer.offerDescription,
            "refer_url": str(e.genericOffer.id)

            })
    for e in shorttermOnceOffers:
        facilities.append(
            {
            "lat": e.genericOffer.lat,
            "type": "Kurzzeit (einmalig)",
            "lng": e.genericOffer.lng,
            "children": e.numberOfChildrenToCare,
            "location": e.genericOffer.location or "N/A",
            "gender": e.get_gender_shortterm_display(),
            "bb": e.genericOffer.bb,
            "offerDescription": e.genericOffer.offerDescription,
            "refer_url": str(e.genericOffer.id)

            })
    return JsonResponse(facilities, safe=False) 

def jobOffersJSON(request):
    offers = JobOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "type": e.get_jobType_display(),
        "title": e.jobTitle,
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 

def manpowerOffersJSON(request):
    offers = ManpowerOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities = [{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_manpower_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 

def translationOffersJSON(request):
    offers = TranslationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False)
    facilities =  [{
        "lat": e.genericOffer.lat,
        "firstLanguage": e.firstLanguage.englishName,
        "secondLanguage": e.secondLanguage.englishName,
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers]
    return JsonResponse(facilities, safe=False) 

def genericOffersJSON(request):
    offers = GenericOffer.objects.filter(~Q(offerType = "DO"),
        active = True, isDigital = False
    )
    logger.warning("TOTAL AMOUNT OF OBJECTS: "+str(offers.count()))
    facilities = format_generic_offers(offers)
    return JsonResponse(facilities, safe=False)
def format_generic_offers(entities):
    return [{
        "lat": e.lat,
        "lng": e.lng,
        "location": e.location,
        "bb": e.bb,
        "offerDescription": e.offerDescription,
        "refer_url": str(e.id)
    } for e in entities]

def get_ttl_hash(seconds=300):
    """Return the same value withing `seconds` time period."""
    return round(time.time() / seconds)
