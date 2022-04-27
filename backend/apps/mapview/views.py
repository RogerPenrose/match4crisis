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
from django.utils.translation import gettext_lazy as _

from apps.offers.models import GenericOffer, AccommodationOffer, ManpowerOffer,TransportationOffer, TranslationOffer, WelfareOffer, BuerocraticOffer, JobOffer, ChildcareOffer
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
    accommodationCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="AC", requestForHelp = False).count()
    transportationCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="TR", requestForHelp = False).count()
    buerocraticCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="BU", requestForHelp = False).count()
    jobCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="JO", requestForHelp = False).count()
    medicalCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="WE", requestForHelp = False).count()
    translationCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="TL", requestForHelp = False).count()
    manpowerCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="MP", requestForHelp = False).count()
    childcareCount = GenericOffer.objects.filter(Q(offerType = "CL")|Q(offerType="BA"),active= True, isDigital = False, requestForHelp = False ).count()
    
    accommodationRequestCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="AC", requestForHelp = True).count()
    transportationRequestCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="TR", requestForHelp = True).count()
    buerocraticRequestCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="BU", requestForHelp = True).count()
    jobRequestCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="JO", requestForHelp = True).count()
    medicalRequestCount =  GenericOffer.objects.filter(active= True, isDigital = False, offerType="WE", requestForHelp = True).count()
    translationRequestCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="TL", requestForHelp = True).count()
    manpowerRequestCount = GenericOffer.objects.filter(active= True, isDigital = False, offerType="MP", requestForHelp = True).count()
    childcareRequestCount = GenericOffer.objects.filter(Q(offerType = "CL")|Q(offerType="BA"),active= True, isDigital = False, requestForHelp = True ).count()
    context = { "entryCount": {"buerocratic": buerocraticCount,"manpower": manpowerCount, "accommodation": accommodationCount, "transportation": transportationCount, "translation": translationCount, "childcare": childcareCount, "medical": medicalCount, "job": jobCount ,
    "buerocraticRequests": buerocraticRequestCount,"manpowerRequests": manpowerRequestCount, "accommodationRequests": accommodationRequestCount, "transportationRequests": transportationRequestCount, "translationRequests": translationRequestCount, "childcareRequests": childcareRequestCount, "medicalRequests": medicalRequestCount, "jobRequests": jobRequestCount }}
    #"accommodation" :request.GET.get("accommodation") == 'True', "transportation": request.GET.get("transportation") == 'True',  "translation": request.GET.get("translation")  == 'True',  "generic": request.GET.get("generic")  == 'True'}
    context.update(request.GET.dict())
    logger.warning("rendering mapview JS ? "+str(request.GET.dict()))
    return render(request, 'mapview/mapview.js', context , content_type='text/javascript')
logger = logging.getLogger("django")
# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    startPosition =  [51.13, 10.018]
    zoom = 6
    getString = ""
    for key in request.GET.dict():
        getString += key+"="+request.GET.get(key)+"&"
    logger.warning("Received Request in Mapview: "+str(request.GET))
    if request.GET.get("city"):
        startPosition = getCenterOfCity(request.GET.get("city"))
        zoom = 10
        logger.warning("Received: "+str(startPosition))
    context = {
    "startPosition":  startPosition,
    "zoom": zoom,
    "mapbox_token": settings.MAPBOX_TOKEN,
    "get_params": getString[:-1]
    }
    context.update(request.GET.dict())
    return render(request, "mapview/map.html", context )
def generalInformationJSON(request):
    returnVal = {
        "offerCount": GenericOffer.objects.filter(~Q(offerType="DO"),active=True, requestForHelp=False, isDigital=False).count(),
        "requestCount":GenericOffer.objects.filter(~Q(offerType="DO"),active=True, requestForHelp=True, isDigital=False).count()
    }
    return JsonResponse(returnVal)
def accommodationOffersJSON(request):
    offers = AccommodationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp = False)
    requests = AccommodationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp = True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "numberOfPeople": e.numberOfPeople,
        "petsAllowed": _("Ja") if e.petsAllowed else _("Nein"),
        "type": e.get_typeOfResidence_display(),
        "startDate": str(e.startDateAccommodation),
        "lng": e.genericOffer.lng,
        "title": e.genericOffer.offerTitle,
        "location": e.genericOffer.location,
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "numberOfPeople": e.numberOfPeople,
        "petsAllowed": _("Ja") if e.petsAllowed else _("Nein"),
        "type": e.get_typeOfResidence_display(),
        "startDate": str(e.startDateAccommodation),
        "lng": e.genericOffer.lng,
        "title": e.genericOffer.offerTitle,
        "location": e.genericOffer.location,
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) # safe=False is needed to return Arrays
    
def transportationOffersJSON(request):
    offers = TransportationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = TransportationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities ={"offers": [{
        "lat": e.genericOffer.lat,
        "distance": e.distance or "N/A",
        "detail": "Passagiere :" + str(e.numberOfPassengers) if e.helpType_transport == "PT" else "Fahrzeugtyp:"+e.get_typeOfCar_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "helpType_transport": e.get_helpType_transport_display(),
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests": [{
        "lat": e.genericOffer.lat,
        "distance": e.distance or "N/A",
        "detail": "Passagiere :" + str(e.numberOfPassengers) if e.helpType_transport == "PT" else "Fahrzeugtyp:"+e.get_typeOfCar_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "helpType_transport": e.get_helpType_transport_display(),
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 
 
def medicalOffersJSON(request):
    offers = WelfareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = WelfareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_welfare_display(),
        "lng": e.genericOffer.lng,
        "title": e.genericOffer.offerTitle,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_welfare_display(),
        "lng": e.genericOffer.lng,
        "title": e.genericOffer.offerTitle,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 
 
def buerocraticOffersJSON(request):
    offers = BuerocraticOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = BuerocraticOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_buerocratic_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_buerocratic_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 


def childcareOffersJSON(request):
    offers = ChildcareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = ChildcareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_childcare_display(),
        "lng": e.genericOffer.lng,
        "children": e.numberOfChildren,
        "location": "Hat Räumlichkeiten" if e.hasSpace else str(e.distance)+"km Umkreis",
        "educated":"Hat eine Ausbildung" if e.hasEducation else "",
        "experience":"Hat Erfahrung" if e.hasExperience else "",
        "title": e.genericOffer.offerTitle,
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "type": e.get_helpType_childcare_display(),
        "lng": e.genericOffer.lng,
        "children": e.numberOfChildren,
        "location": "Hat Räumlichkeiten" if e.hasSpace else str(e.distance)+"km Umkreis",
        "educated":"Hat eine Ausbildung" if e.hasEducation else "",
        "experience":"Hat Erfahrung" if e.hasExperience else "",
        "title": e.genericOffer.offerTitle,
        "bb": e.genericOffer.bb,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    logger.warning("CHildcare: "+str(facilities))
    return JsonResponse(facilities, safe=False) 

def jobOffersJSON(request):
    offers = JobOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = JobOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "type": e.get_jobType_display() ,
        "title": e.jobTitle,
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "type": e.get_jobType_display(),
        "title": e.jobTitle,
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 

def manpowerOffersJSON(request):
    offers = ManpowerOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = ManpowerOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities = {"offers":[{
        "lat": e.genericOffer.lat,
        "type": e.get_distanceChoices_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],
    "requests":[{
        "lat": e.genericOffer.lat,
        "type": e.get_distanceChoices_display(),
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 

def translationOffersJSON(request):
    offers = TranslationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    requests = TranslationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    facilities =  {"offers":[{
        "lat": e.genericOffer.lat,
        "languages": [language.englishName for language in e.languages.all()],
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in offers],"requests":[{
        "lat": e.genericOffer.lat,
        "languages": [language.englishName for language in e.languages.all()],
        "lng": e.genericOffer.lng,
        "location": e.genericOffer.location or "N/A",
        "bb": e.genericOffer.bb,
        "title": e.genericOffer.offerTitle,
        "offerDescription": e.genericOffer.offerDescription,
        "refer_url": str(e.genericOffer.id)
    } for e in requests]}
    logger.warning("Langauges: "+str(facilities["offers"][0]))
    return JsonResponse(facilities, safe=False) 

def genericOffersJSON(request):
    offers = GenericOffer.objects.filter(~Q(offerType = "DO"),
        active = True, isDigital = False, requestForHelp = False
    )
    requests = GenericOffer.objects.filter(~Q(offerType = "DO"),
        active = True, isDigital = False, requestForHelp = True
    )
    logger.warning("TOTAL AMOUNT OF OBJECTS: "+str(offers.count()))
    facilities = {"offers":format_generic_offers(offers), "requests": format_generic_offers(requests)}
    
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
