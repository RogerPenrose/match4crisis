from functools import lru_cache
import time
from django.shortcuts import get_object_or_404,render
import logging
import json
from os.path import dirname, abspath, join

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.gzip import gzip_page

from apps.offers.models import GenericOffer, AccomodationOffer, TransportationOffer, TranslationOffer
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
    context = { "accomodation" :request.GET.get("accomodation") == 'True', "transportation": request.GET.get("transportation") == 'True',  "translation": request.GET.get("translation")  == 'True',  "generic": request.GET.get("generic")  == 'True'}
    logger.warning("rendering mapview JS ? "+str(request.GET))
    return render(request, 'mapview/mapview.js', context , content_type='text/javascript')
logger = logging.getLogger("django")
# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    locations_and_number = prepare_offers(ttl_hash=get_ttl_hash()) # @todo: not sure if this caching still does anything with how we fetch our stuff.. 
    startPosition =  [51.13, 10.018]
    zoom = 6
    logger.warning("Received Request in Mapview: "+str(request.GET))
    if request.GET.get("city"):
        startPosition = getCenterOfCity(request.GET.get("city"))
        zoom = 10
        logger.warning("Received: "+str(startPosition))
    context = {
    "locations": [],
    "mapbox_token": settings.MAPBOX_TOKEN,
    "startPosition":  startPosition,
    "zoom": zoom,
        "accomodation" :request.GET.get("accomodation") == 'True', "transportation": request.GET.get("transportation") == 'True',  "translation": request.GET.get("translation")  == 'True',  "generic": request.GET.get("generic")  == 'True'
    }
    return render(request, "mapview/map.html", context )


@lru_cache(maxsize=1)
def prepare_offers(ttl_hash=None):
    # Source: https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live
    del ttl_hash  # to emphasize we don't use it and to shut pylint up
    offers = GenericOffer.objects.filter(active=True, isDigital= False)
    locations_and_number = {}
    i = 0
    for offer in offers:
        cc = offer.country
        plz = offer.postCode
        key = cc + "_" + plz
        try:
            if key in locations_and_number:
                locations_and_number[cc + "_" + plz]["count"] += 1
            else:
                lat, lon, ort = plzs[cc][plz]
                locations_and_number[key] = {
                    "countrycode": cc,
                    "plz": plz,
                    "count": 1,
                    "lat": lat,
                    "lon": lon,
                    "ort": ort,
                    "i": i,
                }
                i += 1
        except Exception:
            continue
    return locations_and_number

def accomodationOffersJSON(request):
    offers = GenericOffer.objects.filter(active = True, isDigital = False, offerType="AC")
    facilities = group_by_zip_code(offers)
    return JsonResponse(facilities)
    
def transportationOffersJSON(request):
    offers = GenericOffer.objects.filter(active = True, isDigital = False, offerType="TR")
    facilities = group_by_zip_code(offers)
    return JsonResponse(facilities)

def translationOffersJSON(request):
    offers = GenericOffer.objects.filter(active = True, isDigital = False, offerType="TL")
    facilities = group_by_zip_code(offers)
    return JsonResponse(facilities)

def genericOffersJSON(request):
    offers = GenericOffer.objects.filter(
        active = True, isDigital = False
    )
    facilities = group_by_zip_code(offers)
    return JsonResponse(facilities)


def group_by_zip_code(entities):
    countrycode_plz_details = {}

    for entity in entities:
        countrycode = entity.country
        plz = entity.postCode

        if countrycode not in countrycode_plz_details:
            countrycode_plz_details[countrycode] = {}

        country = countrycode_plz_details[countrycode]
        if plz not in country:
            country[plz] = {
                "countrycode": countrycode,
                "plz": plz,
                "count": 0,
                **get_plz_data(countrycode, plz),
            }

        country[plz]["count"] += 1
    return countrycode_plz_details


def get_ttl_hash(seconds=300):
    """Return the same value withing `seconds` time period."""
    return round(time.time() / seconds)
