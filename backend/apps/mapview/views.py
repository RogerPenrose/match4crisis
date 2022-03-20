from functools import lru_cache
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.gzip import gzip_page
from apps.mapview.utils import get_plz_data, plzs


# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    template = loader.get_template("mapview/map.html")
    context = {
        "locations": [],
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))
    
def get_mapJSON(request, type, filter={}):
    objects_to_display = type.objects.filter(
        **filter
    )
    objects_zipped = group_by_zip_code(objects_to_display)
    return JsonResponse(objects_zipped)

def group_by_zip_code(entities):
    countrycode_plz_details = {}

    for entity in entities:
        countrycode = entity.countrycode
        plz = entity.plz

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
