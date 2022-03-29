from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.accounts.views import DashboardView
from apps.offers.models import GenericOffer, getSpecificOffers
from apps.offers.views import mergeImages

def thx(request):
    return render(request, "thanks.html")

class HelperDashboardView(DashboardView):
    template_name = "helper_dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        userOffers = GenericOffer.objects.filter(userId=request.user.id)
        pausedOffers = mergeImages(getSpecificOffers(userOffers.filter(paused=True, incomplete=False)))
        incompleteOffers = mergeImages(getSpecificOffers(userOffers.filter(incomplete=True)))
        runningOffers = mergeImages(getSpecificOffers(userOffers.filter(paused=False, incomplete=False)))


        context = {
            "pausedOffers": pausedOffers,
            "incompleteOffers": incompleteOffers,
            "runningOffers": runningOffers,
        }

        return self.render_to_response(context)


