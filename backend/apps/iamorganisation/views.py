from functools import lru_cache

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.gzip import gzip_page

from apps.accounts.decorator import hospital_required
from apps.iamorganisation.models import Hospital
from apps.mapview.utils import haversine, plzs
from apps.mapview.views import get_ttl_hash

from .forms import PostingForm


#organisation_overview (mapview)
@gzip_page
def hospital_overview(request):
    locations_and_number = prepare_hospitals(ttl_hash=get_ttl_hash(60))
    template = loader.get_template("map_hospitals.html")
    context = {
        "locations": list(locations_and_number.values()),
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))

#list organisations
@lru_cache(maxsize=1)
def prepare_hospitals(ttl_hash=None):
    hospitals = Hospital.objects.filter(
        user__validated_email=True, is_approved=True, appears_in_map=True
    )
    locations_and_number = {}
    for hospital in hospitals:
        if len(hospital.sonstige_infos) != 0:
            cc = hospital.countrycode
            plz = hospital.plz
            key = cc + "_" + plz
            if key in locations_and_number:
                locations_and_number[key]["count"] += 1
                locations_and_number[key]["uuid"] = None
            else:
                lat, lon, ort = plzs[cc][plz]
                locations_and_number[key] = {
                    "uuid": hospital.uuid,
                    "countrycode": cc,
                    "plz": plz,
                    "count": 1,
                    "lat": lat,
                    "lon": lon,
                    "ort": ort,
                }
    return locations_and_number

#list organisations
@login_required
def hospital_list(request, countrycode, plz):

    if countrycode not in plzs or plz not in plzs[countrycode]:
        # TODO: niceren error werfen # noqa: T003
        return HttpResponse(
            "Postleitzahl: " + plz + " ist keine valide Postleitzahl in " + countrycode
        )

    lat, lon, ort = plzs[countrycode][plz]

    table = HospitalTable(
        Hospital.objects.filter(
            user__validated_email=True, is_approved=True, plz=plz, appears_in_map=True
        )
    )
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    context = {"countrycode": countrycode, "plz": plz, "ort": ort, "table": table}

    return render(request, "list_hospitals_by_plz.html", context)


#Anzeige der Organisation
@login_required
@hospital_required
def change_posting(request):
    if request.method == "POST":
        anzeige_form = PostingForm(request.POST, instance=request.user.hospital)

        if anzeige_form.is_valid():
            anzeige_form.save()
            messages.add_message(
                request, messages.INFO, _("Deine Anzeige wurde erfolgreich aktualisiert."),
            )

    else:
        anzeige_form = PostingForm(instance=request.user.hospital)

    context = {"anzeige_form": anzeige_form}
    return render(request, "change_posting.html", context)