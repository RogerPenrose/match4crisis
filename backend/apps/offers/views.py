from django.shortcuts import get_object_or_404,render, redirect
import logging
from os.path import dirname, abspath, join
import json
# Create your views here.
from apps.accounts.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from .models import GenericOffer, AccomodationOffer, TranslationOffer, TransportationOffer, ImageClass, AccompanimentOffer, LegalOffer
from .forms import AccomodationForm, GenericForm, TransportationForm, TranslationForm, ImageForm
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
                isDigital=form.get("isDigital"),  \
                active=form.get("active"),  \
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
            g.isDigital=form.get("isDigital")
            g.active=form.get("active")
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
            numberOfAdults=form.get("numberOfAdults"), \
            numberOfChildren=form.get("numberOfChildren"), \
            typeOfResidence=form.get("typeOfResidence"), \
            numberOfPets=form.get("numberOfPets"), \
            stayLength= form.get("stayLength") )
        a.save()
        return a
    else:
        a = AccomodationOffer.objects.get(pk=offer_id)
        a.genericOffer=g
        a.numberOfAdults=form.get("numberOfAdults")
        a.numberOfChildren=form.get("numberOfChildren")
        a.typeOfResidence=form.get("typeOfResidence")
        a.numberOfPets=form.get("numberOfPets")
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
@login_required
def contact(request, offer_id):
    details = getOfferDetails(request,offer_id)
    return render(request, 'offers/contact.html', details)
def search(request):
    return render(request, 'offers/search.html')
def scrapePostCodeJson(city):

    current_location = dirname(abspath(__file__))
    with open(join(current_location,"files/cities_to_plz.json"), "r") as read_file:
        mappings = json.load(read_file)
        plzs = mappings.get(city.capitalize())
        if plzs is not None:
            return plzs
        else:
            logger.error("NO PLZS FOUND FOR CITY "+city+" Trying for a partial match...")
            for entry in mappings:
                if city.lower() in entry.lower():
                    logger.error("Found a match: "+entry)
                    plzs = mappings.get(entry)
                    return plzs
            
def getCityFromPostCode(postCode):
    current_location = dirname(abspath(__file__))
    with open(join(current_location,"files/plzs_to_cities.json"), "r") as read_file:
        mappings = json.load(read_file)
        return mappings.get(postCode)
def by_city(request, city):
    # Ideally: Associate Postcode with city here...
    #Get list of all PostCodes within the City: 
    postCodes = scrapePostCodeJson(city)
    #Dummy data:
    accomodations= 0
    translations = 0 
    transportations = 0
    accompaniments = 0
    legal = 0
    for postCode in postCodes:
        accomodations += GenericOffer.objects.filter(offerType="AC", postCode=postCode).count()
        translations += GenericOffer.objects.filter(offerType="TL", postCode=postCode).count()
        transportations += GenericOffer.objects.filter(offerType="TR", postCode=postCode).count()
        accompaniments += GenericOffer.objects.filter(offerType="AP", postCode=postCode).count()
        legal += GenericOffer.objects.filter(offerType="LE", postCode=postCode).count()
    totalAccomodations = GenericOffer.objects.filter(offerType="AC").count()
    totalTransportations = GenericOffer.objects.filter(offerType="TR").count()
    totalTranslations = GenericOffer.objects.filter(offerType="TL").count()
    totalAccompaniments = GenericOffer.objects.filter(offerType="AP").count()
    totalLegal = GenericOffer.objects.filter(offerType="LE").count()
    context = {
        'local' : {'AccomodationOffers': accomodations, 'TransportationOffers': transportations, 'TranslationOffers': translations, 'AccompanimentOffers': accompaniments, 'LegalOffers': legal},
        'total' : {'AccomodationOffers': totalAccomodations, 'TransportationOffers': totalTransportations, 'TranslationOffers': totalTranslations, 'LegalOffers': totalLegal},
    }
    logger.warning(str(context))
    return render(request, 'offers/list.html', context)
def by_type(request, offer_type):
    if offer_type== "accomodation":
        context = {"ResultCount": AccomodationOffer.objects.all().count(),
            'Title': "Accommmodations",
            'AccomodationOffers': mergeImages(AccomodationOffer.objects.all())}
    if offer_type== "transportation":
        context = {
            "ResultCount": TransportationOffer.objects.all().count(),'Title': "Transportations", 'TransportationOffers': mergeImages(TransportationOffer.objects.all())}
    if offer_type== "translation":
        context = {
            "ResultCount": TranslationOffer.objects.all().count(),'Title': "Translations",'TranslationOffers': mergeImages(TranslationOffer.objects.all())}
    
    if offer_type== "accompaniment":
        context = {"ResultCount": AccompanimentOffer.objects.all().count(),
            'Title': "Accompaniments",
            'AccompanimentOffers': mergeImages(AccompanimentOffer.objects.all())}
    
    if offer_type== "legal":
        context = {"ResultCount": LegalOffer.objects.all().count(),
            'Title': "Legal",
            'LegalOffers': mergeImages(LegalOffer.objects.all())}
    return render(request, 'offers/index.html', context)
def create_by_filter(request):
    #Below: Lots of convoluted Logic to create a valid filter - Maybe we can automate this more sexily, since we need to add every field here by hand...
    resultVal = {"TransportationOffers":[], "TranslationOffers":[], "AccomodationOffers": [], "AccompanimentOffers":[], "LegalOffers":[]}
    if   request.POST.get("transportation") == "True":
        filters = []
        for key in request.POST:

            if "transportation_" in key:
                if request.POST.get(key) != None and len(request.POST.get(key)) > 0 :
                    filters.append(key.replace("transportation_","")+"="+request.POST.get(key))
        filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
        resultVal["TransportationOffers"] =  eval("mergeImages(TransportationOffer.objects.filter("+filterstring+"))")
    if  request.POST.get("accomodation") == "True":
        filters =[]
        for key in request.POST:
            
            if "accomodation_" in key:
                if request.POST.get(key) != None and len(request.POST.get(key)) > 0 :
                    filters.append(key.replace("accomodation_","")+"="+request.POST.get(key))
        filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
        resultVal["AccomodationOffers"] =  eval("mergeImages(AccomodationOffer.objects.filter("+filterstring+"))")
    if  request.POST.get("translation") == "True":
        filters = []
        for key in request.POST:

            if "translation_" in key:
                if request.POST.get(key) != None and len(request.POST.get(key)) > 0 :
                    filters.append(key.replace("translation_","")+"="+request.POST.get(key))
        filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
        resultVal["TranslationOffers"] =  eval("mergeImages(TranslationOffer.objects.filter("+filterstring+"))")
    
    if  request.POST.get("accompaniment") == "True":
        filters = []
        for key in request.POST:

            if "accompaniment_" in key:
                if request.POST.get(key) != None and len(request.POST.get(key)) > 0 :
                    filters.append(key.replace("accompaniment_","")+"="+request.POST.get(key))
        filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
        resultVal["AccompanimentOffers"] =  eval("mergeImages(AccompanimentOffer.objects.filter("+filterstring+"))")
    if  request.POST.get("legal") == "True":
        filters = []
        for key in request.POST:

            if "legal_" in key:
                if request.POST.get(key) != None and len(request.POST.get(key)) > 0 :
                    filters.append(key.replace("legal_","")+"="+request.POST.get(key))
        filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
        resultVal["LegalOffers"] =  eval("mergeImages(LegalOffer.objects.filter("+filterstring+"))")
        if request.POST.get("translation") == "True" and request.POST.get("accomodation") == "True" and  request.POST.get("transportation") == "True" and  request.POST.get("asccompaniment") == "True" and request.POST.get("legal") == "True":
            resultVal["Title"] = "All Offers"
        else: 
            title = ""
            if request.POST.get("accomodation") == "True":
                title += "Accomodation,"
            if request.POST.get("translation") == "True":
                title += "Translation,"
            if request.POST.get("transportation") == "True":
                title += "Transportation,"               
            if request.POST.get("accompaniment") == "True":
                title += "Accompaniment,"
            if request.POST.get("legal") == "True":
                title += "Legal,"
            title = title[:-1]
            resultVal["Title"] = title
        resultVal["resultCount"] = len(resultVal["TranslationOffers"])+len(resultVal["AccomodationOffers"])+len(resultVal["TranslationOffers"])+len(resultVal["AccompanimentOffers"])+len(resultVal["LegalOffers"])

    return resultVal
def handle_filter(request):
    logger.warning("Received: "+str(request.POST))
    if request.POST.get("show_list") == "True":
        context = create_by_filter(request)
        return render(request, 'offers/index.html', context)
    else :
        query = ""
        if request.POST.get("city"):
            query +="city="+request.POST.get("city")+"&"
        if request.POST.get("accomodation"):
            query +="accomodation=True&"
        else :
            query += "accomodation=False&"
        if request.POST.get("transportation") == "True":
            query +="transportation=True&"
        else :
            query += "transportation=False"
        if request.POST.get("translation") == "True":
            query +="translation=True&"
        else :
            query += "translation=False"
        if request.POST.get("accompaniment") == "True":
            query +="accompaniment=True&"
        else :
            query += "accompaniment=False"
        if request.POST.get("legal") == "True":
            query +="legal=True&"
        else :
            query += "legal=False"
        return redirect("/mapview/?"+query)
        
def list_by_city(request, city):
    postCodes = scrapePostCodeJson(city)
    #Dummy data:
    context = {"ResultCount": GenericOffer.objects.filter(postCode__in=postCodes).count(), 
    'Title': "All Offers",'city': city,
    'TranslationOffers': mergeImages(TranslationOffer.objects.filter(genericOffer__postCode__in=postCodes)),
     'AccomodationOffers': mergeImages(AccomodationOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'AccompanimentOffers': mergeImages(AccompanimentOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'LegalOffers': mergeImages(LegalOffer.objects.filter(genericOffer__postCode__in=postCodes)),
     'TransportationOffers': mergeImages(TransportationOffer.objects.filter(genericOffer__postCode__in=postCodes))}
    return render(request, 'offers/index.html', context)
    
def by_postCode(request, postCode):
    context = {'AccomodationOffers': AccomodationOffer.objects.filter(genericOffer__postCode=postCode), \
               'TransportationOffers': TransportationOffer.objects.filter(genericOffer__postCode=postCode),\
                'AccompanimentOffers': AccompanimentOffer.objects.filter(genericOffer__postCode=postCode), \
                'LegalOffers': LegalOffer.objects.filter(genericOffer__postCode=postCode), \
               'TranslationOffers': TranslationOffer.objects.filter(genericOffer__postCode=postCode)}
    
    return render(request, 'offers/index.html', context)
def mergeImages(offers):
    resultOffers = []
    for entry in  offers: 
        images = ImageClass.objects.filter(offerId= entry.genericOffer.id)
        newEntry =  {
            "image" : None,
            "offer" : entry
        }
        if len(images) > 0:
            newEntry["image"] = images[0].image
        resultOffers.append(newEntry)
    return resultOffers
def index(request):
    accomodationOffers = mergeImages(AccomodationOffer.objects.all())
    accompanimentOffers = mergeImages(AccompanimentOffer.objects.all())
    transportationOffers = mergeImages(TransportationOffer.objects.all())
    translationOffers = mergeImages(TranslationOffer.objects.all())
    legalOffers = mergeImages(LegalOffer.objects.all())


    context = {
        "ResultCount": GenericOffer.objects.all().count(), 
    'Title': "All Offers",
        'AccomodationOffers': accomodationOffers, \
               'TransportationOffers': transportationOffers,\
               'TranslationOffers': translationOffers,\
               'LegalOffers': legalOffers,\
               'AccompanimentOffers': accompanimentOffers}
    
    return render(request, 'offers/index.html', context)

@login_required
def delete_offer(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    if user_is_allowed(request, generic.userId.id):
        generic.delete()
        return index(request )
    else :
        return HttpResponse("Wrong User")
@login_required
def create(request):
    if request.method == 'POST':
        return update(request, 0)
    elif request.method == 'GET':
        form = GenericForm()
        return render(request, 'offers/create.html', {"imageForm": ImageForm(), "genericForm": GenericForm(), "accomodationForm":AccomodationForm(), "transportationForm": TransportationForm(), "translationForm": TranslationForm()})

def update(request, offer_id):
    form = GenericForm(request.POST)
       # form.image = request.FILES
       # logger.warning("Set file: "+str(form.image))
    if form.is_valid():
        logger.warning("FORM IS VALID")
        currentForm = form.cleaned_data
        g = updateGenericModel(currentForm, offer_id, request.user.id)
        if request.FILES.get("image") != None:
            logger.warning("Have file, trying to set.. "+str(request.FILES))
            logger.warning("Trying: "+str(type(offer_id))+" Value: "+str(offer_id))
            image = ImageClass(image=request.FILES.get('image'), offerId = g)
            image.save()
        if g is not None:
            if currentForm.get("offerType") == "AP": # Special case since we have no particular fields in this type.
                offer_id = genericOffer.id
                a = AccompanimentOffer(genericOffer=g)
                a.save()
                return detail(request, offer_id)
            
            elif currentForm.get("offerType") == "LE": # Special case since we have no particular fields in this type.
                offer_id = genericOffer.id
                l = legalOffer(genericOffer=g)
                l.save()
                return detail(request, offer_id)
            elif currentForm.get("offerType") == "AC":
                acForm = AccomodationForm(request.POST)
                if acForm.is_valid():
                    currentForm = acForm.cleaned_data
                    a = updateAccomodationModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(acForm.errors))
            elif currentForm.get("offerType") == "TR":
                trForm = TransportationForm(request.POST)
                if trForm.is_valid():
                    currentForm = trForm.cleaned_data
                    t = updateTransportationModel(g, currentForm, offer_id)
                    offer_id = t.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    
                    return detail(request, offer_id)
                else:
                    return HttpResponse(str(trForm.errors))
            if currentForm.get("offerType") == "TL":
                tlForm = TranslationForm(request.POST)
                if tlForm.is_valid():
                    currentForm = tlForm.cleaned_data
                    t = updateTranslationModel(g, currentForm,offer_id)
                    
                    offer_id = t.genericOffer.id
                    return detail(request, offer_id)
                else:
                    return HttpResponse(str(tlForm.errors))
        else:
            logger.warning("No USER")
            return HttpResponse("Wrong User")
    
    else:
        logger.warning("TEST")
        return HttpResponse(str(form.errors))
def user_is_allowed(request, target_id):
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        user = None
    allowed = False
    if user is not None:
        if request.user.id == target_id or user.is_superuser:
            logger.warning("User is super user: "+str(user.is_superuser))
            allowed = True
        else: 
            logger.warning("User is not authenticated ? "+str(request.user.id)+" VS "+str(target_id))
    return allowed
def delete_image(request, offer_id, image_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    if user_is_allowed(request, generic.userId.id):
        ImageClass.objects.filter(image_id=image_id).delete()
        return detail(request, offer_id, edit_active=True)
    else :
        return HttpResponse("Wrong User")
def getOfferDetails(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    genericForm = GenericForm(instance = generic)
    try:
        imageQuery = ImageClass.objects.filter(offerId=offer_id)
    except ImageClass.DoesNotExist:
        imageQuery = []
    images = []
    for image in imageQuery:
        imageForm = ImageForm()
        imageForm.image = image.image
        imageForm.url = image.image.url
        imageForm.id = image.image_id
        images.append(imageForm)
    allowed = user_is_allowed(request, generic.userId.id)
    city = getCityFromPostCode(generic.postCode)

    if generic.offerType == "AC":
        detail = get_object_or_404(AccomodationOffer, pk=generic.id)
        detailForm = AccomodationForm(model_to_dict(detail))
        return {'offerType': "Accomodation", 'generic': genericForm, 'detail': detailForm, "city": city, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TL":
        detail = get_object_or_404(TranslationOffer, pk=generic.id)
        detailForm = TranslationForm(model_to_dict(detail))
        return {'offerType': "Translation", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TR":
        detail = get_object_or_404(TransportationOffer, pk=generic.id)
        detailForm = TransportationOffer(model_to_dict(detail))
        return {'offerType': "Transportation", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "AP" or generic.OfferType == "LE":
        return {'offerType': "Transportation", 'generic': genericForm, 'detail': None, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 

def detail(request, offer_id, edit_active = False):
    context = getOfferDetails(request, offer_id)
    if edit_active:
        context["edit_active"] = edit_active
    return render(request, 'offers/detail.html', context)
def results(request, offer_id):
    response = "You're looking at the results of offer %s."
    return HttpResponse(response % offer_id)
