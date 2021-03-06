from django.shortcuts import render
from django.utils.decorators import method_decorator

from apps.accounts.views import DashboardView
from apps.ineedhelp.models import Refugee
from apps.offers.models import OFFER_CARD_NAMES, getSpecificOffers, GenericOffer
from apps.accounts.decorator import refugeeRequired

@method_decorator(refugeeRequired, name='dispatch')
class RefugeeDashboardView(DashboardView):
    template_name = "refugee_dashboard.html"

    def get(self, request, *args, **kwargs):
        firstname = request.user.first_name
        hasRequests = GenericOffer.objects.filter(userId=request.user).count() > 0
        userRequests = GenericOffer.objects.filter(userId=request.user)
        incompleteRequests = getSpecificOffers(userRequests.filter(incomplete=True))
        activeRequests =  getSpecificOffers(userRequests.filter(active=True))
        pausedRequests =  getSpecificOffers(userRequests.filter(active=False, incomplete=False))

        context = {
            "firstname": firstname,
            "hasRequests": hasRequests,
            "incompleteRequests" : incompleteRequests,
            "activeRequests" : activeRequests,
            "pausedRequests" : pausedRequests,
            "offercardnames" : OFFER_CARD_NAMES,
        }

        return self.render_to_response(context)

@refugeeRequired
def favouriteOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.favouriteOffers.all())
    return render(request, "favourite_offers.html", {"offers" : offers})
        
@refugeeRequired
def recentlyViewedOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.recentlyViewedOffers.all().order_by('-recentlyviewedintermediary__dateViewed'))
    return render(request, "recently_viewed.html", {"offers" : offers})

@refugeeRequired
def recentlyContactedOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.recentlyContactedOffers.all().order_by('-recentlycontactedintermediary__dateContacted'))
    return render(request, "recently_contacted.html", {"offers" : offers})

@refugeeRequired 
def running_requests(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    runningOffers = getSpecificOffers(userOffers.filter(active=True, incomplete=False))
    context = {"offers": runningOffers}
    return render(request, "running_offers.html", context)
@refugeeRequired 
def paused_requests(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    runningOffers = getSpecificOffers(userOffers.filter(active=False, incomplete=False))
    context = {"offers": runningOffers}
    return render(request, "paused_offers.html", context)
@refugeeRequired 
def incomplete_requests(request):
    userOffers = GenericOffer.objects.filter(userId=request.user.id)
    runningOffers = getSpecificOffers(userOffers.filter(active=False, incomplete=True))
    context = {"offers": runningOffers}
    return render(request, "incomplete_offers.html", context)