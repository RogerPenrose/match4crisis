from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from apps.accounts.views import DashboardView
from apps.offers.models import GenericOffer, getSpecificOffers, OFFER_MODELS
from apps.offers.views import mergeImages
from .forms import ChooseHelpForm
from apps.accounts.decorator import helperRequired
import logging
logger = logging.getLogger("django")

@method_decorator(helperRequired, name='dispatch')
class HelperDashboardView(DashboardView):
    template_name = "helper_dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        pausedOffersCount = GenericOffer.objects.filter(userId=request.user.id, active=False, incomplete=False).count()
        incompleteOffersCount = GenericOffer.objects.filter(userId=request.user.id, incomplete=True).count()
        runningOffersCount = GenericOffer.objects.filter(userId=request.user.id, active=True, incomplete=False).count()
        firstname = request.user.first_name
        userOffers =GenericOffer.objects.filter(userId=request.user.id)
        incompleteOffers = mergeImages(getSpecificOffers(userOffers.filter(incomplete=True)))
        logger.warning("Have incomplete Offers: "+str(len(incompleteOffers)))
        runningOffers =  mergeImages(getSpecificOffers(userOffers.filter(active=True)))
        pausedOffers =  mergeImages(getSpecificOffers(userOffers.filter(active=False, incomplete=False)))

        context = {
            "pausedOffers": pausedOffers,
            "incompleteOffers": incompleteOffers,
            "runningOffers": runningOffers,
            "firstname": firstname
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

            # Filter the POST data to only include the offer information
            for k,v in request.POST.items():
                logger.warning("Key: "+k+" Value: "+v)
                if(k in OFFER_MODELS):
                    # If the offer of type k was selected, set its value to true in the chosenHelp dict, otherwise false
                    chosenHelp[k] = v

            # Add the chosen help data to the request sessions
            request.session['chosenHelp'] = chosenHelp
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
