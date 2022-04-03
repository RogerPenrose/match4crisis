from functools import lru_cache

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.gzip import gzip_page
from apps.accounts.views import DashboardView
import django_tables2 as tables
from django.utils.decorators import method_decorator

from apps.accounts.decorator import organisationRequired
from apps.iamorganisation.models import Organisation
from apps.mapview.utils import haversine, plzs
from apps.mapview.views import get_ttl_hash
from apps.accounts.decorator import organisationRequired

from .forms import PostingForm


#organisation_overview (mapview)
@gzip_page
def organisation_overview(request):
    locations_and_number = prepare_organisations(ttl_hash=get_ttl_hash(60))
    template = loader.get_template("map_organisations.html")
    context = {
        "locations": list(locations_and_number.values()),
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))

#list organisations
@lru_cache(maxsize=1)
def prepare_organisations(ttl_hash=None):
    organisations = Organisation.objects.filter(
        user__validated_email=True, is_approved=True, appears_in_map=True
    )
    locations_and_number = {}
    for organisation in organisations:
        if len(organisation.sonstige_infos) != 0:
            cc = organisation.countrycode
            plz = organisation.plz
            key = cc + "_" + plz
            if key in locations_and_number:
                locations_and_number[key]["count"] += 1
                locations_and_number[key]["uuid"] = None
            else:
                lat, lon, ort = plzs[cc][plz]
                locations_and_number[key] = {
                    "uuid": organisation.uuid,
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
def organisation_list(request, countrycode, plz):

    if countrycode not in plzs or plz not in plzs[countrycode]:
        # TODO: niceren error werfen # noqa: T003
        return HttpResponse(
            "Postleitzahl: " + plz + " ist keine valide Postleitzahl in " + countrycode
        )

    lat, lon, ort = plzs[countrycode][plz]

    table = OrganisationTable(
        Organisation.objects.filter(
            user__validated_email=True, is_approved=True, plz=plz, appears_in_map=True
        )
    )
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    context = {"countrycode": countrycode, "plz": plz, "ort": ort, "table": table}

    return render(request, "list_organisations_by_plz.html", context)


class OrganisationTable(tables.Table):
    info = tables.TemplateColumn(template_name="info_button.html")

    class Meta:
        model = Organisation
        template_name = "django_tables2/bootstrap4.html"
        fields = ["organisationName", "contactPerson"]
        exclude = ["id"]

#Anzeige der Organisation
@login_required
@organisationRequired
def change_posting(request):
    if request.method == "POST":
        anzeige_form = PostingForm(request.POST, instance=request.user.organisation)

        if anzeige_form.is_valid():
            anzeige_form.save()
            messages.add_message(
                request, messages.INFO, _("Deine Anzeige wurde erfolgreich aktualisiert."),
            )

    else:
        anzeige_form = PostingForm(instance=request.user.organisation)

    context = {"anzeige_form": anzeige_form}
    return render(request, "change_posting.html", context)

def thx(request):
    return render(request, "thanks_organisation.html")

@method_decorator(organisationRequired, name='dispatch')
class OrganisationDashboardView(DashboardView):
    template_name = "organisation_dashboard.html"
