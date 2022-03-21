from functools import lru_cache
import time
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.gzip import gzip_page
from apps.offers.models import GenericOffer
from apps.iamstudent.models import Student
from apps.ineedstudent.models import Hospital
from apps.mapview.utils import get_plz_data, plzs



logger = logging.getLogger("django")
# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    locations_and_number = prepare_offers(ttl_hash=get_ttl_hash())
    template = loader.get_template("mapview/map.html")
    context = {
        "locations": list(locations_and_number.values()),
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))


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
    return locations_and_number


def offersJSON(request):
    offers = GenericOffer.objects.filter(
        active = True, isDigital = False
    )
    logger.warning(str(len(offers)))
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
