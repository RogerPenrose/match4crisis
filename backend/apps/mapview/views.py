from functools import lru_cache
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.gzip import gzip_page

from apps.iamstudent.models import Student
from apps.iamorganisation.models import Hospital
from apps.mapview.utils import get_plz_data, plzs


# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    locations_and_number = prepare_students(ttl_hash=get_ttl_hash())
    template = loader.get_template("mapview/map.html")
    context = {
        "locations": list(locations_and_number.values()),
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))


@lru_cache(maxsize=1)
def prepare_students(ttl_hash=None):
    # Source: https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live
    del ttl_hash  # to emphasize we don't use it and to shut pylint up
    students = Student.objects.filter(user__validated_email=True)
    locations_and_number = {}
    i = 0
    for student in students:
        cc = student.countrycode
        plz = student.plz
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


def facilitiesJSON(request):
    hospitals = Hospital.objects.filter(
        user__validated_email=True, is_approved=True, appears_in_map=True
    )
    facilities = group_by_zip_code(hospitals)
    return JsonResponse(facilities)


def supportersJSON(request):
    students = Student.objects.filter(user__validated_email=True)
    supporters = group_by_zip_code(students)
    return JsonResponse(supporters)


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
