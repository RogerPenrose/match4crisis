from django.shortcuts import render
from django.utils.decorators import method_decorator

from apps.accounts.views import DashboardView
from apps.ineedhelp.models import Refugee
from apps.offers.models import getSpecificOffers
from apps.offers.views import mergeImages
from apps.accounts.decorator import refugeeRequired


def thx(request):
    return render(request, "thanks.html")

@method_decorator(refugeeRequired, name='dispatch')
class RefugeeDashboardView(DashboardView):
    template_name = "refugee_dashboard.html"

    def get(self, request, *args, **kwargs):
        firstname = request.user.first_name

        context = {
            "firstname": firstname
        }

        return self.render_to_response(context)

@refugeeRequired
def favouriteOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.favouriteOffers.all())
    return render(request, "favourite_offers.html", {"offers" : mergeImages(offers)})
        
def recentlyViewedOffers(request):
    refugee : Refugee = Refugee.objects.get(user=request.user)
    offers = getSpecificOffers(refugee.recentlyViewedOffers.all().order_by('-recentlyviewedintermediary__dateViewed'))
    return render(request, "recently_viewed.html", {"offers" : mergeImages(offers)})
