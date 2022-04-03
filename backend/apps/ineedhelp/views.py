from django.shortcuts import render
from django.utils.decorators import method_decorator

from apps.accounts.views import DashboardView
from apps.ineedhelp.models import Refugee
from apps.offers.models import getSpecificOffers
from apps.offers.views import mergeImages
from apps.accounts.decorator import refugeeRequired


# Create your views here.

def thx(request):
    return render(request, "thanks.html")

@method_decorator(refugeeRequired, name='dispatch')
class RefugeeDashboardView(DashboardView):
    template_name = "refugee_dashboard.html"

def favouriteOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.favouriteOffers.all())
    return render(request, "favourite_offers.html", {"offers" : mergeImages(offers)})
        