from django.shortcuts import get_object_or_404,render

# Create your views here.
from django.http import HttpResponse
from .models import GenericOffer, AccomodationOffer, TranslationOffer, TransportationOffer

def index(request):
    latest_question_list = GenericOffer.objects.order_by('created_at')[:5]
    context = {'latest_question_list': latest_question_list}
    return HttpResponse(str(context))
    #return render(request, 'index.html', context)

def detail(request, offer_id):
    question = get_object_or_404(GenericOffer, pk=offer_id)
    return render(request, 'detail.html', {'question': question})

def results(request, offer_id):
    response = "You're looking at the results of offer %s."
    return HttpResponse(response % offer_id)

def vote(request, offer_id):
    return HttpResponse("You're voting on question %s." % offer_id)