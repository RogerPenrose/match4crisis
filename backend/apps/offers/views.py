import re
from django.shortcuts import get_object_or_404,render, redirect
import logging
from os.path import dirname, abspath, join
import json
import base64
from apps.accounts.models import User
from django.utils import timezone
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from apps.ineedhelp.models import Refugee
from .models import GenericOffer, AccommodationOffer, TranslationOffer, TransportationOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, WelfareOffer, JobOffer, DonationOffer
from .forms import AccommodationForm, GenericForm, TransportationForm, TranslationForm, ImageForm, BuerocraticForm, ManpowerForm, ChildcareFormLongterm, ChildcareFormShortterm, WelfareForm, JobForm, DonationForm
from django.contrib.auth.decorators import login_required
# Helper object to map some unfortunate misnamings etc and to massively reduce clutter below.      
OFFERTYPESOBJ = { "accommodation": { "title": "Accommodation", "requestName": "accommodation", "modelName" : "AccommodationOffer", "offersName": "AccommodationOffers"}, 
                "transportation": { "title": "Transportation", "requestName": "transportation", "modelName": "TransportationOffer", "offersName": "TransportationOffers"},
                "manpower": { "title": "Manpower", "requestName": "manpower", "modelName": "ManpowerOffer", "offersName": "ManpowerOffers"},
                "buerocratic": { "title" :  "Buerocratic Aide", "requestName": "buerocratic", "modelName": "BuerocraticOffer", "offersName": "BuerocraticOffers"}, 
                "childcareshortterm" : { "title" : "Childcare / Babysitting", "requestName": "childcareshortterm", "modelName": "ChildcareOfferShortterm", "offersName": "ChildcareOffersShortterm"}, 
                "childcarelongterm" : { "title" : "Childcare (Longterm)", "requestName": "childcarelongterm", "modelName": "ChildcareOfferLongterm", "offersName": "ChildcareOffersLongterm"}, 
                "job" : { "title" : "Job", "requestName": "job", "modelName": "JobOffer", "offersName": "JobOffers"}, 
                "welfare" : { "title" : "Medical Assistance", "requestName": "welfare", "modelName": "WelfareOffer", "offersName": "WelfareOffers"},
                "donation" : { "title" : "Donations", "requestName": "donation", "modelName": "DonationOffer", "offersName": "DonationOffers"}}
logger = logging.getLogger("django")
def updateGenericModel( form, offer_id=0, userId=None):
    user = User.objects.get(pk=userId) 
    if offer_id== 0:
        #create an Object..
        g = GenericOffer(userId=user, \
                offerType=form.get("offerType"),  \
                created_at=timezone.now(), \
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
            g.created_at=timezone.now()
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

def updateChildcareShortTermModel(g, form, offer_id=0):
    if offer_id == 0:
        a = ChildcareOfferShortterm(genericOffer=g, \
            numberOfChildrenToCare=form.get("numberOfChildrenToCare"), \
            gender=form.get("gender"), \
            isRegular=form.get("isRegular"))
        a.save()
        return a
    else:
        a = ChildcareOfferShortterm.objects.get(pk=offer_id)
        a.genericOffer=g
        a.numberOfChildrenToCare=form.get("numberOfChildrenToCare")
        a.gender=form.get("gender")
        a.isRegular=form.get("isRegular")
        a.save()
        return a
    
def updateChildcareLongTermModel(g, form, offer_id=0):
    if offer_id == 0:
        a = ChildcareOfferLongterm(genericOffer=g, \
            gender=form.get("gender"))
        a.save()
        return a
    else:
        a = ChildcareOfferLongterm.objects.get(pk=offer_id)
        a.genericOffer=g
        a.gender=form.get("gender")
        a.save()
        return a

def updateAccommodationModel(g, form, offer_id=0):
    if offer_id == 0:
        a = AccommodationOffer(genericOffer=g, \
            numberOfAdults=form.get("numberOfAdults"), \
            numberOfChildren=form.get("numberOfChildren"), \
            typeOfResidence=form.get("typeOfResidence"), \
            numberOfPets=form.get("numberOfPets"), \
            startDateAccommodation= form.get("startDateAccommodation") ,\
            endDateAccommodation= form.get("endDateAccommodation"))
        a.save()
        return a
    else:
        a = AccommodationOffer.objects.get(pk=offer_id)
        a.genericOffer=g
        a.numberOfAdults=form.get("numberOfAdults")
        a.numberOfChildren=form.get("numberOfChildren")
        a.typeOfResidence=form.get("typeOfResidence")
        a.numberOfPets=form.get("numberOfPets")
        a.startDateAccommodation= form.get("startDateAccommodation") 
        a.endDateAccommodation= form.get("endDateAccommodation")
        a.save()
        return a

def updateJobModel(g, form, offer_id=0):
    if offer_id == 0:
        t = JobOffer(genericOffer=g, \
            jobType=form.get("jobType"))
        t.save()
        return t
    else:
        t = JobOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.jobType=form.get("jobType")
        t.requirements=form.get("requirements")
        t.jobTitle=form.get("jobTitle")
        t.save()
        return t
def updateWelfareModel(g, form, offer_id=0):
    if offer_id == 0:
        t = WelfareOffer(genericOffer=g, \
            helpType=form.get("helpType"))
        t.save()
        return t
    else:
        t = WelfareOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType=form.get("helpType")
        t.save()
        return t

def updateDonationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = DonationOffer(genericOffer=g, \
            donationTitle=form.get("donationTitle"),\
            account=form.get("account"))
        t.save()
        return t
    else:
        t = DonationOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.donationTitle=form.get("donationTitle")
        t.account=form.get("account")
        t.save()
        return t

def updateManpowerModel(g, form, offer_id=0):
    if offer_id == 0:
        t = ManpowerOffer(genericOffer=g, \
            helpType=form.get("helpType"))
        t.save()
        return t
    else:
        t = ManpowerOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType=form.get("helpType")
        t.save()
        return t
        
def updateBuerocraticModel(g, form, offer_id=0):
    if offer_id == 0:
        t = BuerocraticOffer(genericOffer=g, \
            helpType=form.get("helpType"))
        t.save()
        return t
    else:
        t = BuerocraticOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType=form.get("helpType")
        t.save()
        return t
    
def updateTransportationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = TransportationOffer(genericOffer=g, \
            postCodeEnd=form.get("postCodeEnd"), \
            streetNameEnd=form.get("streetNameEnd"),\
            streetNumberEnd = form.get("streetNumberEnd"),\
            date = form.get("date"), \
            numberOfPassengers=form.get("numberOfPassengers"))
        t.save()
        return t
    else:
        t = TransportationOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.postCodeEnd=form.get("postCodeEnd")
        t.streetNameEnd=form.get("streetNameEnd")
        t.streetNumberEnd = form.get("streetNumberEnd")
        t.date = form.get("date")
        t.numberOfPassengers=form.get("numberOfPassengers")
        t.save()
        return t
    
def updateTranslationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = TranslationOffer(genericOffer=g, \
                        firstLanguage=form.get("firstLanguage").isoCode, \
                        secondLanguage=form.get("secondLanguage").isoCode)
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
def getTranslationImage(request, firstLanguage, secondLanguage):
    logger.warning("Received:"+firstLanguage+" "+secondLanguage)
    # first load flag from file:
    firstData = ""
    secondData = ""
    p1 = staticfiles_storage.path('img/flags/'+firstLanguage+'.svg')
    with open(p1, "rb") as fileHandle:
        raw = fileHandle.read()
        firstData = base64.b64encode(raw)
    p2 = staticfiles_storage.path('img/flags/'+secondLanguage+'.svg')
    with open(p2, "rb") as fileHandle:
        raw = fileHandle.read()
        secondLanguage = base64.b64encode(raw)
    context = {"firstLanguage" : firstData.decode("utf-8")
, "secondLanguage" : secondLanguage.decode("utf-8")}
    return render(request, 'offers/drawing.svg', context=context,content_type="image/svg+xml")
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
    accommodations= 0
    translations = 0 
    transportations = 0
    buerocratic = 0
    welfare = 0
    childcareShortterm = 0
    for postCode in postCodes:
        accommodations += GenericOffer.objects.filter(offerType="AC", postCode=postCode).count()
        translations += GenericOffer.objects.filter(offerType="TL", postCode=postCode).count()
        transportations += GenericOffer.objects.filter(offerType="TR", postCode=postCode).count()
        accompaniments += GenericOffer.objects.filter(offerType="AP", postCode=postCode).count()
        buerocratic += GenericOffer.objects.filter(offerType="BU", postCode=postCode).count()
        childcareShortterm += GenericOffer.objects.filter(offerType="BA", postCode=postCode).count()
        welfare += GenericOffer.objects.filter(offerType="WE", postCode=postCode).count()
        jobs += GenericOffer.objects.filter(offerType="JO", postCode=postCode).count()
    totalAccommodations = GenericOffer.objects.filter(offerType="AC").count()
    totalTransportations = GenericOffer.objects.filter(offerType="TR").count()
    totalTranslations = GenericOffer.objects.filter(offerType="TL").count()
    totalBuerocratic = GenericOffer.objects.filter(offerType="BU").count()
    totalWelfare = GenericOffer.objects.filter(offerType="WE").count()
    totalChildcareShortterm = GenericOffer.objects.filter(offerType="BA").count()
    totalChildcareLongterm = GenericOffer.objects.filter(offerType="CL").count()
    totalJobs = GenericOffer.objects.filter(offerType="JO").count()
    context = {
        'local' : {'AccommodationOffers': accommodations, 'JobOffers': jobs,'WelfareOffers': welfare, 'TransportationOffers': transportations, 'TranslationOffers': translations, 'BuerocraticOffers': buerocratic, "ChildcareOfferShortterms": childcareShortterm,"ChildcareOfferLongterms": childcareLongterm},
        'total' : {'AccommodationOffers': totalAccommodations, 'JobOffers': totalJobs, 'WelfareOffers': totalWelfare, 'TransportationOffers': totalTransportations, 'TranslationOffers': totalTranslations, 'BuerocraticOffer': totalBuerocratic, 'ChildcareOfferShortterm': totalChildcareShortterm, 'ChildcareOfferLongterm': totalChildcareLongterm},
    }
    logger.warning(str(context))
    return render(request, 'offers/list.html', context)
def by_type(request, offer_type):
    context = { "ResultCount" : eval(OFFERTYPESOBJ[offer_type]["modelName"]+".objects.all().count()"),
                "Title": OFFERTYPESOBJ[offer_type]["title"],
                OFFERTYPESOBJ[offer_type]["offersName"]: eval("mergeImages("+OFFERTYPESOBJ[offer_type]["modelName"]+".objects.all())")}
    return render(request, 'offers/index.html', context)
def create_by_filter(request):
    #Below: Lots of convoluted Logic to create a valid filter - Maybe we can automate this more sexily, since we need to add every field here by hand...
    resultVal = {"TransportationOffers":[], "DonationOffers":[],"TranslationOffers":[], "AccommodationOffers": [],"BuerocraticOffers":[],"ManpowerOffers":[],"ChildcareOffersLongterm":[],"ChildcareOffersShortterm":[],"WelfareOffers":[],"JobOffers":[]}
    titleAll = True
    totalCount = 0
    pagination = False
    pageCount = 0
    if request.POST.get("page") != None and len(request.POST.get("page"))> 0:
        pageCount = int(request.POST.get("page"))
    firstEntry = (pageCount+1)* N_ENTRIES
    lastEntry = pageCount * N_ENTRIES
    for offertype in OFFERTYPESOBJ:
        entry = OFFERTYPESOBJ[offertype]
        if request.POST.get(entry["requestName"]) == "True":
            logger.warning("Trying: "+entry["requestName"])
            filters = []
            for key in request.POST:
                if entry["requestName"]+"_" in key:
                    if request.POST.get(key) != None  and len(request.POST.get(key)) > 0 :
                        filters.append(key.replace(entry["requestName"]+"_","")+"="+request.POST.get(key))
            filterstring = str(filters).replace("'", "").replace("[","").replace("]", "")
            logger.warning("Trying to get: "+filterstring)
            entryCount = eval(entry["modelName"]+".objects.filter("+filterstring+").count()")
            totalCount += entryCount
            if  entryCount < N_ENTRIES:
                resultVal[entry["offersName"]] =  eval("mergeImages("+entry["modelName"]+".objects.filter("+filterstring+"))")
            else:
                resultVal[entry["offersName"]] =  eval("mergeImages("+entry["modelName"]+".objects.filter("+filterstring+")["+str(lastEntry)+":"+str(firstEntry)+"])")
                logger.warning("PAGINATION ADDED")
                pagination = True
        else:
            titleAll = False
    if  titleAll:
        resultVal["Title"] = "All Offers"
    else: 
        title = ""
        for entry in OFFERTYPESOBJ:
            if request.POST.get(entry) == "True":
                title += OFFERTYPESOBJ[entry]["title"]+","
        title = title[:-1]
        resultVal["Title"] = title
    resultVal["ResultCount"] = totalCount
    resultVal["page"] = str(int(pageCount)+1) # Off by one Error in frontend..
    resultVal["maxPage"] = str(int(totalCount/N_ENTRIES))
    resultFilter = {}
    for key in dict(request.POST):
        resultFilter[key] = dict(request.POST)[key][0]
    resultVal["currentFilter"] = json.dumps(resultFilter)
    logger.warning("Current Filter: "+str(resultVal["currentFilter"]))
    resultVal["pagination"] = pagination
    return resultVal


def handle_filter(request):
    if request.POST.get("show_list") == "True":
        context = create_by_filter(request)
        return render(request, 'offers/index.html', context)
    else :
        query = ""
        for entry in OFFERTYPESOBJ:
            if request.POST.get(entry) == "True":
                query +=entry+"=True&"
            else:
                query += entry+"=False&"
        if request.POST.get("city"):
            query +="city="+request.POST.get("city")+"&"
        return redirect("/mapview/?"+query)
        
def list_by_city(request, city):
    postCodes = scrapePostCodeJson(city)
    #Dummy data:
    context = {"ResultCount": GenericOffer.objects.filter(postCode__in=postCodes).count(), 
    'Title': "All Offers",'city': city,
    'TranslationOffers': mergeImages(TranslationOffer.objects.filter(genericOffer__postCode__in=postCodes)),
     'AccommodationOffers': mergeImages(AccommodationOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'BuerocraticOffers': mergeImages(BuerocraticOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'ManpowerOffers': mergeImages(ManpowerOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'DonationOffers': mergeImages(DonationOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'ChildcareOffersShortterm': mergeImages(ChildcareOfferShortterm.objects.filter(genericOffer__postCode__in=postCodes)), 
     'ChildcareOffersLongterm': mergeImages(ChildcareOfferLongterm.objects.filter(genericOffer__postCode__in=postCodes)), 
     'WelfareOffers': mergeImages(WelfareOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'JobOffers': mergeImages(JobOffer.objects.filter(genericOffer__postCode__in=postCodes)), 
     'TransportationOffers': mergeImages(TransportationOffer.objects.filter(genericOffer__postCode__in=postCodes))}
    return render(request, 'offers/index.html', context)
    
def by_postCode(request, postCode):
    context = {'AccommodationOffers': mergeImages(AccommodationOffer.objects.filter(genericOffer__postCode=postCode)), \
               'TransportationOffers': mergeImages(TransportationOffer.objects.filter(genericOffer__postCode=postCode)),\
               'ManpowerOffers': mergeImages(ManpowerOffer.objects.filter(genericOffer__postCode=postCode)),\
               'DonationOffers': mergeImages(DonationOffer.objects.filter(genericOffer__postCode=postCode)),\
                'BuerocraticOffers': mergeImages(BuerocraticOffer.objects.filter(genericOffer__postCode=postCode)), 
     'ChildcareOffersShortterm': mergeImages(ChildcareOfferShortterm.objects.filter(genericOffer__postCode=postCode)), 
     'ChildcareOffersLongterm': mergeImages(ChildcareOfferLongterm.objects.filter(genericOffer__postCode=postCode)), 
     'JobOffers': mergeImages(JobOffer.objects.filter(genericOffer__postCode=postCode)), 
     'WelfareOffers': mergeImages(WelfareOffer.objects.filter(genericOffer__postCode=postCode)), 
               'TranslationOffers': mergeImages(TranslationOffer.objects.filter(genericOffer__postCode=postCode))}
    
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
N_ENTRIES = 25 # Number of Entries that are calculated per category (to reduce load.. )
def index(request):
    accommodationOffers = mergeImages(AccommodationOffer.objects.all()[:N_ENTRIES])
    buerocraticOffers = mergeImages(BuerocraticOffer.objects.all()[:N_ENTRIES])
    transportationOffers = mergeImages(TransportationOffer.objects.all()[:N_ENTRIES])
    translationOffers = mergeImages(TranslationOffer.objects.all()[:N_ENTRIES])
    manpowerOffers = mergeImages(ManpowerOffer.objects.all()[:N_ENTRIES])
    donationOffers = mergeImages(DonationOffer.objects.all()[:N_ENTRIES])
    ChildcareOffersLongterm = mergeImages(ChildcareOfferLongterm.objects.all()[:N_ENTRIES])
    ChildcareOffersShortterm = mergeImages(ChildcareOfferShortterm.objects.all()[:N_ENTRIES])
    WelfareOffers = mergeImages(WelfareOffer.objects.all()[:N_ENTRIES])
    JobOffers = mergeImages(JobOffer.objects.all()[:N_ENTRIES])
    manpowerOffers = mergeImages(ManpowerOffer.objects.all()[:N_ENTRIES])
    pagination = False
    maxPage = int(GenericOffer.objects.all().count()/N_ENTRIES)
    currentElements = {}
    for key in OFFERTYPESOBJ:
        currentElements[key] = "True"
    currentFilter = json.dumps(currentElements)
    if maxPage > 1:
        pagination = True
    context = {
        "currentFilter" :json.dumps(currentElements),
        "pagination": pagination,
        "maxPage": maxPage,
        "page": 1,
        "ResultCount": GenericOffer.objects.all().count(), 
    'Title': "All Offers",
        'AccommodationOffers': accommodationOffers, \
               'TransportationOffers': transportationOffers,\
               'TranslationOffers': translationOffers,\
               'ManpowerOffers': manpowerOffers,\
               'DonationOffers': donationOffers,\
               'ChildcareOffersLongterm': ChildcareOffersLongterm,\
               'ChildcareOffersShortterm': ChildcareOffersShortterm,\
               'WelfareOffers': WelfareOffers,\
               'JobOffers': JobOffers,\
               'BuerocraticOffers': buerocraticOffers}
    
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
        return render(request, 'offers/create.html', {"imageForm": ImageForm(),"jobForm": JobForm(), "genericForm": GenericForm(), "accommodationForm":AccommodationForm(), "manpowerForm":ManpowerForm(),"buerocraticForm": BuerocraticForm(), "transportationForm": TransportationForm(), "translationForm": TranslationForm(), "childcarelongtermForm": ChildcareFormLongterm(), "childcareshorttermForm": ChildcareFormShortterm(), 'welfareForm': WelfareForm(), 'donationForm': DonationForm()})

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
            if currentForm.get("offerType") == "MP": # Special case since we have no particular fields in this type.
                buForm = ManpowerForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateManpowerModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(buForm.errors))
            if currentForm.get("offerType") == "DO": # Special case since we have no particular fields in this type.
                buForm = DonationForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateDonationModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(buForm.errors))
            if currentForm.get("offerType") == "WE": # Special case since we have no particular fields in this type.
                weForm = WelfareForm(request.POST)
                if weForm.is_valid():
                    currentForm = weForm.cleaned_data
                    a = updateWelfareModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(weForm.errors))
            if currentForm.get("offerType") == "JO": # Special case since we have no particular fields in this type.
                joForm = JobForm(request.POST)
                if joForm.is_valid():
                    currentForm = joForm.cleaned_data
                    a = updateJobModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(joForm.errors))
            if currentForm.get("offerType") == "BA": # Special case since we have no particular fields in this type.
                baForm = ChildcareFormShortterm(request.POST)
                if baForm.is_valid():
                    currentForm = baForm.cleaned_data
                    a = updateChildcareShortTermModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(baForm.errors))
            if currentForm.get("offerType") == "CL": # Special case since we have no particular fields in this type.
                clForm = ChildcareFormLongterm(request.POST)
                if clForm.is_valid():
                    currentForm = clForm.cleaned_data
                    a = updateChildcareLongTermModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(clForm.errors))
            if currentForm.get("offerType") == "BU": # Special case since we have no particular fields in this type.
                buForm = BuerocraticForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateBuerocraticModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning("Object empty")
                    return HttpResponse(str(buForm.errors))
            elif currentForm.get("offerType") == "AC":
                acForm = AccommodationForm(request.POST)
                if acForm.is_valid():
                    currentForm = acForm.cleaned_data
                    a = updateAccommodationModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    logger.warning("Offer ID: "+str(offer_id))
                    return detail(request, offer_id)
                else:
                    logger.warning(str(request.POST))
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
        detail = get_object_or_404(AccommodationOffer, pk=generic.id)
        detailForm = AccommodationForm(model_to_dict(detail))
        return {'offerType': "Accommodation", 'generic': genericForm, 'detail': detailForm, "city": city, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "WE":
        detail = get_object_or_404(WelfareOffer, pk=generic.id)
        detailForm = WelfareForm(model_to_dict(detail))
        return {'offerType': "Medical Assistance", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TL":
        detail = get_object_or_404(TranslationOffer, pk=generic.id)
        detailForm = TranslationForm(model_to_dict(detail))
        return {'offerType': "Translation", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TR":
        detail = get_object_or_404(TransportationOffer, pk=generic.id)
        detailForm = TransportationOffer(model_to_dict(detail))
        return {'offerType': "Transportation", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "MP":
        detail = get_object_or_404(ManpowerOffer, pk=generic.id)
        detailForm = ManpowerForm(model_to_dict(detail))
        return {'offerType': "Manpower", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "DO":
        detail = get_object_or_404(DonationOffer, pk=generic.id)
        detailForm = DonationForm(model_to_dict(detail))
        return {'offerType': "Donations", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "BA":
        detail = get_object_or_404(ChildcareOfferShortterm, pk=generic.id)
        detailForm = ChildcareFormShortterm(model_to_dict(detail))
        return {'offerType': "Babysitting", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "CL":
        detail = get_object_or_404(ChildcareOfferLongterm, pk=generic.id)
        detailForm = ChildcareFormLongterm(model_to_dict(detail))
        return {'offerType': "Childcare Longterm", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "JO":
        detail = get_object_or_404(JobOffer, pk=generic.id)
        detailForm = JobForm(model_to_dict(detail))
        return {'offerType': "Job", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "BU":
        detail = get_object_or_404(BuerocraticOffer, pk=generic.id)
        detailForm = BuerocraticForm(model_to_dict(detail))
        return {'offerType': "Buerocratic", 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 

def detail(request, offer_id, edit_active = False):
    context = getOfferDetails(request, offer_id)
    if edit_active:
        context["edit_active"] = edit_active
    if request.user.is_authenticated and request.user.isRefugee:
        # If the current user is a Refugee: Check if they have favourited this offer and add it to the recently viewed offers
        offer = GenericOffer.objects.get(pk=offer_id)
        context["favourited"] = offer.favouritedBy.filter(user=request.user)
        refugee = Refugee.objects.get(user=request.user)
        refugee.addRecentlyViewedOffer(offer)
    return render(request, 'offers/detail.html', context)
def results(request, offer_id):
    response = "You're looking at the results of offer %s."
    return HttpResponse(response % offer_id)

def vote(request, offer_id):
    return HttpResponse("You're voting on question %s." % offer_id)

def ajax_toggle_favourite(request):
    if not request.is_ajax() or not request.method=='POST':
        return HttpResponseNotAllowed(['POST'])
    else:
        try:
            offer = GenericOffer.objects.get(pk=request.POST["offerId"])
            refugee = Refugee.objects.get(user=request.user)
            favourited = refugee.toggleFavourite(offer)

            return JsonResponse({"success":True, "favourited":favourited})

        except (Exception):
            return JsonResponse({"success":False})
