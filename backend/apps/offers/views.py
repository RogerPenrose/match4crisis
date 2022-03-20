from django.shortcuts import get_object_or_404,render
# Create your views here.
from apps.accounts.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from .models import GenericOffer, AccomodationOffer, TranslationOffer, TransportationOffer
from .forms import AccomodationForm, GenericForm, TransportationForm, TranslationForm
from datetime import datetime, timedelta
def index(request):
    context = {'AccomodationOffers': AccomodationOffer.objects.all(), \
               'TransportationOffers': TransportationOffer.objects.all(),\
               'TranslationOffers': TranslationOffer.objects.all()}
    
    return render(request, 'offers/index.html', context)
def create(request):
    if request.method == 'POST':
        form = GenericForm(request.POST)
        #return HttpResponse(str(request.POST))
        if form.is_valid():
            currentForm = form.cleaned_data
            user = User.objects.get(pk=1) # Need to fix this to the currently logged in user.
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
                cost=currentForm.get("cost"), \
                )
            g.save()
            if currentForm.get("offerType") == "AC":
                acForm = AccomodationForm(request.POST)
                if acForm.is_valid():
                    currentForm = acForm.cleaned_data
                    a = AccomodationOffer(genericOffer=g, \
                        numberOfInhabitants=currentForm.get("inhabitants"), \
                        petsAllowed=currentForm.get("petsAllowed"), \
                        stayLength= currentForm.get("stayLength") )
                    a.save()
                    return HttpResponse("Thanks")
                else:
                    return HttpResponse(str(acForm.errors))
            elif currentForm.get("offerType") == "TR":
                trForm = TransportationForm(request.POST)
                if trForm.is_valid():
                    currentForm = trForm.cleaned_data
                    t = TransportationOffer(genericOffer=g, \
                        postCodeEnd=currentForm.get("postCodeEnd"), \
                        streetNameEnd=currentForm.get("streetNameEnd"),\
                        streetNumberEnd = currentForm.get("streetNumberEnd"),\
                        typeOfCar = currentForm.get("typeOfCar"), \
                        numberOfPassengers=currentForm.get("numberOfPassengers"))
                    t.save()
                    return HttpResponse("Thanks")
                else:
                    return HttpResponse(str(trForm.errors))
            if currentForm.get("offerType") == "TL":
                tlForm = TranslationForm(request.POST)
                if tlForm.is_valid():
                    currentForm = tlForm.cleaned_data
                    t = TranslationOffer(genericOffer=g, \
                        firstLanguage=currentForm.get("firstLanguage"), \
                        secondLanguage=currentForm.get("secondLanguage"))
                    t.save()
                    return HttpResponse("Thanks")
                else:
                    return HttpResponse(str(tlForm.errors))
        
        else:
            return HttpResponse(str(form.errors))
    elif request.method == 'GET':
        form = GenericForm()
        return render(request, 'offers/create.html', {"genericForm": GenericForm(), "accomodationForm":AccomodationForm(), "transportationForm": TransportationForm(), "translationForm": TranslationForm()})
def detail(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    genericForm = GenericForm(model_to_dict(generic))
    
    if generic.offerType == "AC":
        detail = get_object_or_404(AccomodationOffer, pk=generic.id)
        detailForm = AccomodationForm(model_to_dict(detail))
        return render(request, 'offers/detail.html', {'generic': genericForm, 'detail': detailForm, "id": generic.id})
    if generic.offerType == "TL":
        detail = get_object_or_404(TranslationOffer, pk=generic.id)
        detailForm = TranslationForm(model_to_dict(detail))
        return render(request, 'offers/detail.html', {'generic': genericForm, 'detail': detailForm, "id": generic.id})
    if generic.offerType == "TR":
        detail = get_object_or_404(TransportationOffer, pk=generic.id)
        detailForm = TransportationOffer(model_to_dict(detail))
        return render(request, 'offers/detail.html', {'generic': genericForm, 'detail': detailForm, "id": generic.id})

def results(request, offer_id):
    response = "You're looking at the results of offer %s."
    return HttpResponse(response % offer_id)

def vote(request, offer_id):
    return HttpResponse("You're voting on question %s." % offer_id)