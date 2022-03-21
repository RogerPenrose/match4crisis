from django.shortcuts import get_object_or_404,render
import logging
# Create your views here.
from apps.accounts.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from .models import GenericOffer, AccomodationOffer, TranslationOffer, TransportationOffer
from .forms import AccomodationForm, GenericForm, TransportationForm, TranslationForm
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required



logger = logging.getLogger("django")
def updateGenericModel( form, offer_id=0, userId=None):
    user = User.objects.get(pk=userId) 
    if offer_id== 0:
        #create an Object..
        g = GenericOffer(userId=user, \
                offerType=form.get("offerType"),  \
                created_at=datetime.now(), \
                offerDescription=form.get("offerDescription"), \
                isDigital=False,  \
                active=False,  \
                country=form.get("country"), \
                postCode=form.get("postCode"), \
                streetName=form.get("streetName"), \
                streetNumber=form.get("streetNumber"), \
                cost=form.get("cost"), \
                )
        g.save()
        return g
    else:
        g = GenericOffer.objects.get(pk=offer_id)
        if g.userId.id == userId or user.is_superuser :# If the same user is there to edit OR the user is a superuser...
            g.offerType=form.get("offerType")
            g.created_at=datetime.now()
            g.offerDescription=form.get("offerDescription")
            g.isDigital=False
            g.active=False
            g.country=form.get("country")
            g.postCode=form.get("postCode")
            g.streetName=form.get("streetName")
            g.streetNumber=form.get("streetNumber")
            g.cost=form.get("cost")
            g.save()
            return g
        else:
            logger.warning("Not allowed to update")
            return None

def updateAccomodationModel(g, form, offer_id=0):
    if offer_id == 0:
        a = AccomodationOffer(genericOffer=g, \
            numberOfInhabitants=form.get("numberOfInhabitants"), \
            petsAllowed=form.get("petsAllowed"), \
            stayLength= form.get("stayLength") )
        a.save()
        return a
    else:
        a = AccomodationOffer.objects.get(pk=offer_id)
        a.genericOffer=g
        a.numberOfInhabitants=form.get("numberOfInhabitants")
        a.petsAllowed=form.get("petsAllowed")
        a.stayLength= form.get("stayLength")
        a.save()
        return a

def updateTransportationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = TransportationOffer(genericOffer=g, \
            postCodeEnd=form.get("postCodeEnd"), \
            streetNameEnd=form.get("streetNameEnd"),\
            streetNumberEnd = form.get("streetNumberEnd"),\
            typeOfCar = form.get("typeOfCar"), \
            numberOfPassengers=form.get("numberOfPassengers"))
        t.save()
        return t
    else:
        t = TransportationOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.postCodeEnd=form.get("postCodeEnd")
        t.streetNameEnd=form.get("streetNameEnd")
        t.streetNumberEnd = form.get("streetNumberEnd")
        t.typeOfCar = form.get("typeOfCar")
        t.numberOfPassengers=form.get("numberOfPassengers")
        t.save()
        return t
    
def updateTranslationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = TranslationOffer(genericOffer=g, \
                        firstLanguage=form.get("firstLanguage"), \
                        secondLanguage=form.get("secondLanguage"))
        t.save()
        return t
    else:
        t = TranslationOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.firstLanguage=form.get("firstLanguage")
        t.secondLanguage=form.get("secondLanguage")
        t.save()
        return t
def index(request):
    context = {'AccomodationOffers': AccomodationOffer.objects.all(), \
               'TransportationOffers': TransportationOffer.objects.all(),\
               'TranslationOffers': TranslationOffer.objects.all()}
    
    return render(request, 'offers/index.html', context)
@login_required
def create(request):
    if request.method == 'POST':
        update(request, 0)
    elif request.method == 'GET':
        form = GenericForm()
        return render(request, 'offers/create.html', {"genericForm": GenericForm(), "accomodationForm":AccomodationForm(), "transportationForm": TransportationForm(), "translationForm": TranslationForm()})

def update(request, offer_id):
    form = GenericForm(request.POST)
    if form.is_valid():
        currentForm = form.cleaned_data
        g = updateGenericModel(currentForm, offer_id, request.user.id)
        if g is not None:
            if currentForm.get("offerType") == "AC":
                acForm = AccomodationForm(request.POST)
                if acForm.is_valid():
                    currentForm = acForm.cleaned_data
                    a = updateAccomodationModel(g, currentForm, offer_id)
                    
                    return index(request)
                else:
                    return HttpResponse(str(acForm.errors))
            elif currentForm.get("offerType") == "TR":
                trForm = TransportationForm(request.POST)
                if trForm.is_valid():
                    currentForm = trForm.cleaned_data
                    t = updateTransportationModel(g, currentForm, offer_id)
                    
                    return index(request)
                else:
                    return HttpResponse(str(trForm.errors))
            if currentForm.get("offerType") == "TL":
                tlForm = TranslationForm(request.POST)
                if tlForm.is_valid():
                    currentForm = tlForm.cleaned_data
                    t = updateTranslationModel(g, currentForm,offer_id)
                    return index(request)
                else:
                    return HttpResponse(str(tlForm.errors))
        else:
            return HttpResponse("Wrong User")
    
    else:
        return HttpResponse(str(form.errors))

        
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