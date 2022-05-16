from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from apps.iamorganisation.models import HelpRequest
from apps.iamorganisation.filters import HelpRequestFilter
from apps.accounts.views import DashboardView
from apps.accounts.decorator import helperRequired
from apps.offers.models import OFFER_CARD_NAMES, GenericOffer, getSpecificOffers, OFFER_MODELS
from apps.offers.views import mergeImages

from .forms import ChooseHelpForm
from .models import Helper
import logging

logger = logging.getLogger("django")


@method_decorator(helperRequired, name='dispatch')
class HelperDashboardView(DashboardView):
    template_name = "helper_dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        firstname = request.user.first_name
        userOffers =GenericOffer.objects.filter(userId=request.user.id)
        incompleteOffers = mergeImages(getSpecificOffers(userOffers.filter(incomplete=True)))
        logger.warning("Have incomplete Offers: "+str(len(incompleteOffers)))
        activeOffers =  mergeImages(getSpecificOffers(userOffers.filter(active=True)))
        pausedOffers =  mergeImages(getSpecificOffers(userOffers.filter(active=False, incomplete=False)))

        context = {
            "pausedOffers": pausedOffers,
            "incompleteOffers": incompleteOffers,
            "activeOffers": activeOffers,
            "firstname": firstname,
            "offercardnames" : OFFER_CARD_NAMES,
        }

        return self.render_to_response(context)


def choose_help(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ChooseHelpForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            chosenHelp = {}
            chosenHelpSubchoices = {}

            # Filter the POST data to only include the offer information
            for k in request.POST:
                if(k in OFFER_MODELS):
                    # If the offer of type k was selected, set its value to true in the chosenHelp dict, otherwise false
                    chosenHelp[k] = request.POST.get(k)
                elif(k.endswith("Subchoices")):
                    # Add the subchoices in case there are any
                    chosenHelpSubchoices[k[:2]] = request.POST.getlist(k)

            # Add the chosen help data to the request sessions
            request.session['chosenHelp'] = chosenHelp
            request.session['chosenHelpSubchoices'] = chosenHelpSubchoices

            return HttpResponseRedirect("/accounts/signup_helper")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseHelpForm()

    return render(request, "choose_help.html", {"form": form})

@login_required
@helperRequired
def paused_offers(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    pausedOffers = mergeImages(getSpecificOffers(userOffers.filter(active=False, incomplete=False)))
    context = {"offers": pausedOffers}
    return render(request, "paused_offers.html", context)

@login_required
@helperRequired
def incomplete_offers(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    incompleteOffers = getSpecificOffers(userOffers.filter(incomplete=True))
    context = {"offers": incompleteOffers}
    return render(request, "incomplete_offers.html", context)

@login_required
@helperRequired  
def running_offers(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    logger.warning("Getting: "+str(userOffers.count()))
    for offer in userOffers:
        logger.warning("Type: "+offer.get_offerType_display())
    runningOffers = mergeImages(getSpecificOffers(userOffers.filter(active=True, incomplete=False)))
    context = {"offers": runningOffers}
    return render(request, "running_offers.html", context)

@login_required
@helperRequired
def help_requests_view(request):
    HELP_REQUEST_PER_PAGE = 25
    helper = Helper.objects.get(user=request.user)
    helpRequests = HelpRequest.objects.all()
    filter = HelpRequestFilter(request.GET, queryset=helpRequests)
    paginator = Paginator(list(filter.qs), HELP_REQUEST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj" : page_obj,
        "filter" : filter,
    }
    return render(request, "help_requests_overview.html", context)