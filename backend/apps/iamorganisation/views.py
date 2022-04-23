from functools import lru_cache

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.gzip import gzip_page
from apps.accounts.views import DashboardView
import django_tables2 as tables
from django.utils.decorators import method_decorator

from apps.accounts.decorator import organisationRequired
from apps.iamorganisation.models import DonationRequest, HelpRequest, Image, Organisation
from apps.mapview.utils import haversine, plzs
from apps.mapview.views import get_ttl_hash
from apps.accounts.decorator import organisationRequired

from .forms import DonationRequestForm, HelpRequestForm


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
        user__validated_email=True, isApproved=True, appears_in_map=True
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
            user__validated_email=True, isApproved=True, plz=plz, appears_in_map=True
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

def thx(request):
    return render(request, "thanks_organisation.html")

@method_decorator(organisationRequired, name='dispatch')
class OrganisationDashboardView(DashboardView):
    template_name = "organisation_dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        organisation = Organisation.objects.get(user = request.user)

        context = {
            "organisation" : organisation
        }

        return self.render_to_response(context)

@login_required
@organisationRequired
def request_help(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST)

        if form.is_valid():
            # TODO add logic for actually sending out emails
            recipientCount = 42 # TODO how many helpers were contacted

            helpRequestEntry = form.save(commit=False)
            helpRequestEntry.organisation = Organisation.objects.get(user=request.user)
            helpRequestEntry.recipientCount = recipientCount
            helpRequestEntry.save()

            if request.FILES.get("images") is not None:
                counter = 0
                images = request.FILES.getlist('images')
                for image in images:
                    counter = counter + 1
                    image = Image(image=image, request = helpRequestEntry)
                    image.save()

            context = {"recipientCount" : recipientCount} 
            return render(request, "request_sent.html", context)

    else:
        form = HelpRequestForm()

    context = {"form" : form}
    return render(request, "request_help.html", context)


@login_required
@organisationRequired
def create_donation_request(request):
    if request.method == "POST":
        form = DonationRequestForm(request.POST)

        if form.is_valid():

            donationRequestEntry = form.save(commit=False)
            donationRequestEntry.organisation = Organisation.objects.get(user=request.user)
            donationRequestEntry.save()

            if request.FILES.get("images") is not None:
                counter = 0
                images = request.FILES.getlist('images')
                for image in images:
                    counter = counter + 1
                    image = Image(image=image, request = donationRequestEntry)
                    image.save()

            context = {}
            return render(request, "donation_request_created.html", context)

    else:
        form = DonationRequestForm()

    context = {"form" : form}
    return render(request, "request_donations.html", context)


@login_required
@organisationRequired
def sent_requests(request):
    requests = HelpRequest.objects.filter(organisation=Organisation.objects.get(user=request.user))
    context = {"helpRequests" : requests}
    return render(request, "sent_requests.html", context)

def organisation_overview(request):
    orgs = Organisation.objects.filter(isApproved=True)
    context = {
        "organisations" : orgs,
    }
    return render(request, "organisation_overview.html", context)

def donation_detail(request, donation_request_id):
    donationRequest = DonationRequest.objects.get(pk=donation_request_id)
    organisation = donationRequest.organisation
    images = Image.objects.filter(request=donationRequest)
    context = {
        "donationRequest" : donationRequest, 
        "organisation" : organisation, 
        "images" : images if images.count() > 0 else None
    }
    return render(request, "donation_detail.html", context)