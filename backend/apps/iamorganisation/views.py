from functools import lru_cache
from itertools import chain

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.decorators.gzip import gzip_page
from apps.accounts.views import DashboardView
import django_tables2 as tables
from django_filters.views import FilterView
from django.utils.decorators import method_decorator

from apps.accounts.models import User
from apps.accounts.decorator import helperRequired, organisationRequired
from apps.mapview.utils import haversine, plzs
from apps.mapview.views import get_ttl_hash
from apps.offers.models import GenericOffer, ManpowerOffer
from apps.iofferhelp.models import Helper

from .models import DonationRequest, HelpRequest, Image, MaterialDonationRequest, Organisation
from .forms import ContactHelpRequestForm, DonationRequestForm, HelpRequestForm, MaterialDonationRequestForm
from .filters import DonationRequestFilter
from .utils import send_email_to_organisation, send_help_request_emails


# CONSTANTS
ORGANISATIONS_PER_PAGE = 10
DONATIONS_PER_PAGE = 10

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

@method_decorator(organisationRequired, name='dispatch')
class OrganisationDashboardView(DashboardView):
    template_name = "organisation_dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        organisation = Organisation.objects.get(user = request.user)

        donationRequests = list(chain(DonationRequest.objects.filter(organisation=organisation), MaterialDonationRequest.objects.filter(organisation=organisation)))
        helpRequests = HelpRequest.objects.filter(organisation=organisation)


        context = {
            "organisation" : organisation,
            "donationRequests" : donationRequests,
            "helpRequests" : helpRequests,
            "editAllowed" : True,
        }

        return self.render_to_response(context)

@login_required
@organisationRequired
def request_help(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST)

        if form.is_valid():

            organisation = Organisation.objects.get(user=request.user)

            helpRequestEntry = form.save(commit=False)
            helpRequestEntry.organisation = organisation

            offers = GenericOffer.objects.filter(offerType="MP", requestForHelp=False)
            users = User.objects.filter(genericoffer__in=offers).distinct()

            recipientCount = users.count()

            helpRequestEntry.recipientCount = recipientCount
            helpRequestEntry.save()

            send_help_request_emails(organisation, helpRequestEntry, users, get_current_site(request).domain)

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
def edit_help_request(request, help_request_id):
    helpRequest = get_object_or_404(HelpRequest, pk=help_request_id)
    organisation = Organisation.objects.get(user=request.user)
    if helpRequest.organisation != organisation:
        raise PermissionDenied

    if request.method == "POST":
        form = HelpRequestForm(request.POST, instance=helpRequest)

        if form.is_valid():
            form.save()

            if request.FILES.get("images") is not None:
                counter = 0
                images = request.FILES.getlist('images')
                for image in images:
                    counter = counter + 1
                    image = Image(image=image, request = helpRequest)
                    image.save()

            return redirect('help_request_detail', help_request_id = help_request_id)

    form = HelpRequestForm(instance=helpRequest)
    form.helper.form_action = "edit"
    context = {"form" : form, "edit" : True}
    return render(request, "request_help.html", context)

@login_required
@organisationRequired
def delete_help_request(request, help_request_id):
    helpRequest = get_object_or_404(HelpRequest, pk=help_request_id)
    organisation = Organisation.objects.get(user=request.user)
    if helpRequest.organisation != organisation:
        raise PermissionDenied
    helpRequest.delete()
    return redirect("login_redirect")

@login_required
@organisationRequired
def request_donations(request):
    return render(request, "select_donation_type.html")

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

    context = {"form" : form, "edit" : False, "isMaterial" : False}
    return render(request, "request_donations.html", context)


@login_required
@organisationRequired
def edit_donation_request(request, donationRequest):
    #donationRequest = get_object_or_404(DonationRequest, pk=donation_request_id)
    organisation = Organisation.objects.get(user=request.user)
    if donationRequest.organisation != organisation:
        raise PermissionDenied

    if request.method == "POST":
        form = DonationRequestForm(request.POST, instance=donationRequest)

        if form.is_valid():
            form.save()

            if request.FILES.get("images") is not None:
                counter = 0
                images = request.FILES.getlist('images')
                for image in images:
                    counter = counter + 1
                    image = Image(image=image, request = donationRequest)
                    image.save()

            return redirect('donation_detail', donation_request_id = donationRequest.pk)

    form = DonationRequestForm(instance=donationRequest)
    form.helper.form_action = "edit"
    context = {"form" : form, "edit" : True, "isMaterial" : False}
    return render(request, "request_donations.html", context)

@login_required
@organisationRequired
def delete_donation_request(request, donation_request_id):
    try:
        donationRequest = DonationRequest.objects.get(pk=donation_request_id)
    except DonationRequest.DoesNotExist:
        donationRequest = MaterialDonationRequest.objects.get(pk=donation_request_id)
    organisation = Organisation.objects.get(user=request.user)
    if donationRequest.organisation != organisation:
        raise PermissionDenied
    donationRequest.delete()
    return redirect("login_redirect")

@login_required
@organisationRequired
def create_material_donation_request(request):
    if request.method == "POST":
        form = MaterialDonationRequestForm(request.POST)

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
        form = MaterialDonationRequestForm()

    context = {"form" : form, "edit" : False, "isMaterial" : True}
    return render(request, "request_donations.html", context)


@login_required
@organisationRequired
def edit_material_donation_request(request, donationRequest):
    #donationRequest = get_object_or_404(MaterialDonationRequest, pk=material_donation_request_id)
    organisation = Organisation.objects.get(user=request.user)
    if donationRequest.organisation != organisation:
        raise PermissionDenied

    if request.method == "POST":
        form = MaterialDonationRequestForm(request.POST, instance=donationRequest)

        if form.is_valid():
            form.save()

            if request.FILES.get("images") is not None:
                counter = 0
                images = request.FILES.getlist('images')
                for image in images:
                    counter = counter + 1
                    image = Image(image=image, request = donationRequest)
                    image.save()

            return redirect('donation_detail', donation_request_id = donationRequest.pk)

    form = MaterialDonationRequestForm(instance=donationRequest)
    form.helper.form_action = "edit"
    context = {"form" : form, "edit" : True, "isMaterial" : True}
    return render(request, "request_donations.html", context)

@login_required
@organisationRequired
def edit_redirect(request, donation_request_id):
    try:
        donationRequest = DonationRequest.objects.get(pk=donation_request_id)
        return edit_donation_request(request, donationRequest)
    except DonationRequest.DoesNotExist:
        donationRequest = MaterialDonationRequest.objects.get(pk=donation_request_id)
        return edit_material_donation_request(request, donationRequest)


@login_required
@organisationRequired
def sent_requests(request):
    requests = HelpRequest.objects.filter(organisation=Organisation.objects.get(user=request.user))
    context = {"helpRequests" : requests}
    return render(request, "sent_requests.html", context)

class OrganisationOverview(ListView):
    paginate_by = ORGANISATIONS_PER_PAGE
    model = Organisation
    queryset = Organisation.objects.filter(isApproved=True)
    template_name = "organisation_overview.html"

def donation_overview(request):
    donationRequests = DonationRequest.objects.filter(organisation__isApproved = True)
    materialDonationRequests = MaterialDonationRequest.objects.filter(organisation__isApproved = True)
    filterMoney = DonationRequestFilter(request.GET, queryset=donationRequests)
    filterMaterial = DonationRequestFilter(request.GET, queryset=materialDonationRequests)
    filters = list(chain(filterMoney.qs, filterMaterial.qs))
    paginator = Paginator(filters, DONATIONS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj" : page_obj,
        "donationsCount" : len(filters),
        "filter" : filterMoney,
    }
    return render(request, "donations.html", context)

def donation_detail(request, donation_request_id):
    try:
        donationRequest = DonationRequest.objects.get(pk=donation_request_id)
        isMaterial = False
    except DonationRequest.DoesNotExist:
        donationRequest = get_object_or_404(MaterialDonationRequest, pk=donation_request_id)
        isMaterial = True
    organisation = donationRequest.organisation
    images = Image.objects.filter(request=donationRequest)
    editAllowed = request.user.is_authenticated and request.user.isOrganisation and donationRequest.organisation == Organisation.objects.get(user = request.user)

    context = {
        "donationRequest" : donationRequest, 
        "organisation" : organisation, 
        "images" : images if images.count() > 0 else None,
        "editAllowed" : editAllowed,
        "isMaterial" : isMaterial,
    }
    return render(request, "donation_detail.html", context)

@login_required
def help_request_detail(request, help_request_id, contacted=False):
    helpRequest = get_object_or_404(HelpRequest, pk=help_request_id)
    organisation = helpRequest.organisation
    images = Image.objects.filter(request=helpRequest)
    editAllowed = request.user.is_authenticated and request.user.isOrganisation and helpRequest.organisation == Organisation.objects.get(user = request.user)

    context = {
        "helpRequest" : helpRequest, 
        "organisation" : organisation, 
        "images" : images if images.count() > 0 else None,
        "editAllowed" : editAllowed,
        "contacted" : contacted,
    }
    return render(request, "help_request_detail.html", context)

    
@login_required
@helperRequired
def contact_help_request(request, help_request_id):

    if request.method == "POST":
        form = ContactHelpRequestForm(request.POST)

        if form.is_valid():
            helpRequest = get_object_or_404(HelpRequest, pk=help_request_id)
            helper = Helper.objects.get(user=request.user)
            recipient = helpRequest.organisation
            send_email_to_organisation(helper, helpRequest, form.cleaned_data["message"], get_current_site(request).domain)

            #TODO Add this offer to the helper's recently contacted offers
            # refugee.addRecentlyContactedOffer(offer)
            return help_request_detail(request, help_request_id, contacted = True)
    else:
        form = ContactHelpRequestForm()
        return render(request, 'contact_help_request.html', {"form" : form})
