from django.shortcuts import get_object_or_404,render

# Create your views here.
from apps.accounts.models import User
from django.http import HttpResponse
from .models import GenericOffer, AccomodationOffer, TranslationOffer, TransportationOffer
from .forms import AccomodationForm, GenericForm
from datetime import datetime, timedelta
def index(request):
    latest_question_list = AccomodationOffer.objects.all()
    context = {'latest_question_list': latest_question_list}
    return HttpResponse(str(context))
    #return render(request, 'index.html', context)
def create(request):
    if request.method == 'POST':
        form = GenericForm(request.POST)
        if form.is_valid():
           # return HttpResponse(str(form.cleaned_data))
            currentForm = form.cleaned_data
            user = User.objects.get(pk=1)
            g = GenericOffer(userId=user, \
                offerType=currentForm.get("offerType"),  \
                created_at=datetime.now(), \
                offerDescription=currentForm.get("offerDescription"), \
                isDigital=False,  \
                active=False,  \
                country=currentForm.get("country"), \
                postCode=currentForm.get("postCode"), \
                streetName=currentForm.get("streetName"), \
                streetNumber=currentForm.get("streetNumber"), \
                )
            g.save()
            if currentForm.get("offerType") == "AC":
                a = AccomodationOffer(newGenericOffer=g, \
                    numberOfInhabitants=currentForm.get("inhabitants"), \
                    petsAllowed=currentForm.get("petsAllowed"), \
                    cost= currentForm.get("cost"), stayLength= timedelta(days=currentForm.get("stayLength")) )
                a.save()
                return HttpResponse(str(a))
            elif currentForm.get("offerType") == "TL":
                t = TransportationOffer(newGenericOffer=g, \
                    postCodeEnd=currentForm.get("postCodeEnd"), \
                    streetNameEnd=currentForm.get("streetNameEnd"),\
                    streetNumberEnd = currentForm.get("streetNumberEnd"),\
                    typeOfCar = currentForm.get("typeOfCar"),\
                    cost = currentForm.get("cost"),\
                    petsAllowed = currentForm.get("petsAllowed"))
                t.save()
                return HttpResponse(str(t))
            if currentForm.get("offerType") == "TR":
                t = TranslationOffer(newGenericOffer=g, \
                    firstLanguage=currentForm.get("firstLanguage"), \
                    secondLanguage=currentForm.get("secondLanguage"))
                t.save()
                return HttpResponse(str(t))
    elif request.method == 'GET':
        form = GenericForm()
        return render(request, 'offers/create.html', {"form": form})
def detail(request, offer_id):
    question = get_object_or_404(GenericOffer, pk=offer_id)
    return render(request, 'detail.html', {'question': question})

def results(request, offer_id):
    response = "You're looking at the results of offer %s."
    return HttpResponse(response % offer_id)

def vote(request, offer_id):
    return HttpResponse("You're voting on question %s." % offer_id)