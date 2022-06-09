from itertools import chain
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from apps.accounts.views import DashboardView
from django.utils.decorators import method_decorator

from apps.accounts.models import User
from apps.accounts.decorator import helperRequired, organisationRequired
from apps.offers.models import GenericOffer
from apps.iofferhelp.models import Helper

from .models import DonationRequest, HelpRequest, Image, MaterialDonationRequest, Organisation
from .forms import ContactHelpRequestForm, DonationRequestForm, HelpRequestForm, MaterialDonationRequestForm
from .filters import DonationRequestFilter
from .utils import send_email_to_organisation, send_help_request_emails


# CONSTANTS
ORGANISATIONS_PER_PAGE = 20
DONATIONS_PER_PAGE = 20

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

            # TODO filter by location / distance to organisation
            offers = GenericOffer.objects.filter(offerType="MP", requestForHelp=False, active=True, incomplete=False)
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

            request.session["recipientCount"] = recipientCount
            return redirect('help_requests_created')

    else:
        form = HelpRequestForm()

    context = {"form" : form}
    return render(request, "request_help.html", context)


@login_required
@organisationRequired
def help_requests_created(request):
    return render(request, "request_sent.html", {"recipientCount" : request.session["recipientCount"]})

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

            return redirect('donation_request_created')

    else:
        form = DonationRequestForm()

    context = {"form" : form, "edit" : False, "isMaterial" : False}
    return render(request, "request_donations.html", context)


@login_required
@organisationRequired
def donation_request_created(request):
    return render(request, "donation_request_created.html")

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
