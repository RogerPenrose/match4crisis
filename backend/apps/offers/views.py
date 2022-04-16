import re
from django.shortcuts import get_object_or_404,render, redirect
import logging
from os.path import dirname, abspath, join
import json
import googlemaps
import math
import base64
from apps.accounts.models import User
from django.utils import timezone
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from apps.ineedhelp.models import Refugee
from apps.accounts.decorator import refugeeRequired
from .filters import GenericFilter, AccommodationFilter, TranslationFilter, TransportationFilter, BuerocraticFilter, ManpowerFilter,  ChildCareFilterLongterm, ChildCareFilterShortterm, WelfareFilter, JobFilter
from .models import GenericOffer, AccommodationOffer, TranslationOffer, TransportationOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, WelfareOffer, JobOffer, DonationOffer
from .forms import AccommodationForm, GenericForm, TransportationForm, TranslationForm, ImageForm, BuerocraticForm, ManpowerForm, ChildcareFormLongterm, ChildcareFormShortterm, WelfareForm, JobForm, DonationForm
from django.contrib.auth.decorators import login_required

gmaps = googlemaps.Client(key='AIzaSyAuyDEd4WZh-OrW8f87qmS-0sSrY47Bblk')
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
                offerTitle = form.get("offerTitle"), \
                created_at=timezone.now(), \
                offerDescription=form.get("offerDescription"), \
                isDigital=form.get("isDigital"),  \
                active=form.get("active"),  \
                lat=form.get("lat"), \
                lng=form.get("lng"), \
                bb=form.get("bb"), \
                cost=form.get("cost"), \
                )
        g.save()
        return g
    else:
        g = GenericOffer.objects.get(pk=offer_id)
        if g.userId.id == userId or user.is_superuser :# If the same user is there to edit OR the user is a superuser...
            g.offerType=form.get("offerType")
            g.offerTitle=form.get("offerTitle")
            g.created_at=timezone.now()
            g.offerDescription=form.get("offerDescription")
            g.isDigital=form.get("isDigital")
            g.active=form.get("active")
            g.lat=form.get("lat")
            g.lng=form.get("lng")
            g.bb=form.get("bb")
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
            gender_shortterm=form.get("gender_shortterm"), \
            isRegular=form.get("isRegular"))
        a.save()
        return a
    else:
        a = ChildcareOfferShortterm.objects.get(pk=offer_id)
        a.genericOffer=g
        a.numberOfChildrenToCare=form.get("numberOfChildrenToCare")
        a.gender_shortterm=form.get("gender_shortterm")
        a.isRegular=form.get("isRegular")
        a.save()
        return a
    
def updateChildcareLongTermModel(g, form, offer_id=0):
    if offer_id == 0:
        a = ChildcareOfferLongterm(genericOffer=g, \
            gender_longterm=form.get("gender_longterm"))
        a.save()
        return a
    else:
        a = ChildcareOfferLongterm.objects.get(pk=offer_id)
        a.genericOffer=g
        a.gender=form.get("gender_longterm")
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
            helpType_welfare=form.get("helpType_welfare"))
        t.save()
        return t
    else:
        t = WelfareOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType_welfare=form.get("helpType_welfare")
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
            helpType_manpower=form.get("helpType_manpower"))
        t.save()
        return t
    else:
        t = ManpowerOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType_manpower=form.get("helpType_manpower")
        t.save()
        return t
        
def updateBuerocraticModel(g, form, offer_id=0):
    if offer_id == 0:
        t = BuerocraticOffer(genericOffer=g, \
            helpType_buerocratic=form.get("helpType_buerocratic"))
        t.save()
        return t
    else:
        t = BuerocraticOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.helpType_buerocratic=form.get("helpType_buerocratic")
        t.save()
        return t
    
def updateTransportationModel(g, form, offer_id=0):
    if offer_id == 0:
        t = TransportationOffer(genericOffer=g, \
            locationEnd=form.get("locationEnd"), \
            latEnd=form.get("latEnd"),\
            lngEnd = form.get("lngEnd"),\
            bbEnd = form.get("bbEnd"),\
            date = form.get("date"), \
            numberOfPassengers=form.get("numberOfPassengers"))
        t.save()
        return t
    else:
        t = TransportationOffer.objects.get(pk=offer_id)
        t.genericOffer=g
        t.locationEnd=form.get("locationEnd")
        t.latEnd=form.get("latEnd")
        t.lngEnd = form.get("lngEnd")
        t.bbEnd = form.get("bbEnd")
        t.date = form.get("date")
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
def getCityBbFromLocation(locationData):
    reverse_geocode_result = gmaps.geocode(locationData)
    returnVal = {
    "latMin": reverse_geocode_result[0]["geometry"]["bounds"]["southwest"]["lat"], 
    "lngMin": reverse_geocode_result[0]["geometry"]["bounds"]["southwest"]["lng"], 
    "lngMax": reverse_geocode_result[0]["geometry"]["bounds"]["northeast"]["lng"], 
    "latMax": reverse_geocode_result[0]["geometry"]["bounds"]["northeast"]["lat"],}
    
    for x in reverse_geocode_result[0]['address_components']:
        if 'locality' in x["types"]:
            returnVal["city"] = x["long_name"]
    
    logger.warning(str(returnVal))
    
    return returnVal

def getCityFromCoordinates(locationData):
    reverse_geocode_result = gmaps.reverse_geocode(locationData)
    returnVal = {}
    for entry in reverse_geocode_result:
        if "administrative_area_level_2" in entry["types"]:
            returnVal = {
            "latMin": entry["geometry"]["bounds"]["southwest"]["lat"], 
            "lngMin": entry["geometry"]["bounds"]["southwest"]["lng"], 
            "lngMax": entry["geometry"]["bounds"]["northeast"]["lng"], 
            "latMax": entry["geometry"]["bounds"]["northeast"]["lat"],}
    for x in reverse_geocode_result[0]['address_components']:
        if 'locality' in x["types"]:
            returnVal["city"] = x["long_name"]
    
    return returnVal

def kmInLng(km, lat):
    lng = float(km)/111.320*math.cos(math.radians(lat))
    return float(lng)
def kmInLat(km):
    lat = float(km)/110.574
    return float(lat)

@login_required
@refugeeRequired
def contact(request, offer_id):
    if request.method == "POST":
        # TODO send email

        # If the current user is a Refugee: Add this offer to their recently contacted offers
        if request.user.is_authenticated and request.user.isRefugee:
            offer = GenericOffer.objects.get(pk=offer_id)
            refugee = Refugee.objects.get(user=request.user)
            refugee.addRecentlyContactedOffer(offer)
        return HttpResponseRedirect(request.path[:-len("/contact")])
    else:
        details = getOfferDetails(request,offer_id)
        return render(request, 'offers/contact.html', details)

def search(request):
    # Ideally: Associate Postcode with city here...
    #Get list of all PostCodes within the City: 
    city = ""
    lngMax = 0
    lngMin = 0
    latMax = 0
    latMin = 0
    rangeKm = request.GET.get("range")
    if request.GET.get("lat") == "" and request.GET.get("location")  is not None: 
        locationData = getCityBbFromLocation(request.GET.get("location"))
        city = locationData["city"]
        lngMax = float(locationData["lngMax"])+kmInLng(rangeKm, locationData["latMax"])
        latMin = float(locationData["latMin"])-kmInLat(rangeKm)
        lngMin = float(locationData["lngMin"])-kmInLng(rangeKm,  locationData["latMax"])
        latMax = locationData["latMax"]+kmInLat(rangeKm )
    elif request.GET.get("lat") is not None: 
        bb = json.loads(request.GET.get("bb"))
        locationData = { "city": request.GET.get("location"), "lngMax": bb["east"], "lngMin": bb["west"], "latMax": bb["north"], "latMin": bb["south"]}
        city = locationData["city"]
        lngMax = locationData["lngMax"]+kmInLng(rangeKm, locationData["latMax"])
        latMin = locationData["latMin"]-kmInLat(rangeKm)
        lngMin = locationData["lngMin"]-kmInLng(rangeKm, locationData["latMax"])
        latMax = locationData["latMax"]+kmInLat(rangeKm)
    #location = getCityBbFromLocation(locationData)
    #Dummy data:
    logger.warning("LNG:"+str(lngMin)+"-"+str(lngMax)+"LAT:"+str(latMin)+"-"+str(latMax))
    accommodations = GenericOffer.objects.filter(active=True,offerType="AC", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    translations = GenericOffer.objects.filter(active=True,offerType="TL", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    transportations = GenericOffer.objects.filter(active=True,offerType="TR", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    accompaniments = GenericOffer.objects.filter(active=True,offerType="AP", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    buerocratic = GenericOffer.objects.filter(active=True,offerType="BU", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    childcareShortterm = GenericOffer.objects.filter(active=True,offerType="BA", lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    welfare = WelfareOffer.objects.filter(genericOffer__active=True,helpType_welfare__in=["ELD","DIS"], genericOffer__lat__range=(latMin, latMax), genericOffer__lng__range=(lngMin, lngMax)).count()
    psych = WelfareOffer.objects.filter(genericOffer__active=True,helpType_welfare="PSY", genericOffer__lat__range=(latMin, latMax), genericOffer__lng__range=(lngMin, lngMax)).count()
    jobs = GenericOffer.objects.filter(active=True,offerType="JO",  lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    childcareLongterm = GenericOffer.objects.filter(active=True,offerType="CL",  lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    manpower = GenericOffer.objects.filter(active=True,offerType="MP",  lat__range=(latMin, latMax), lng__range=(lngMin, lngMax)).count()
    totalAccommodations = GenericOffer.objects.filter(active=True,offerType="AC").count()
    totalTransportations = GenericOffer.objects.filter(active=True,offerType="TR").count()
    totalTranslations = GenericOffer.objects.filter(active=True,offerType="TL").count()
    totalBuerocratic = GenericOffer.objects.filter(active=True,offerType="BU").count()
    totalWelfare = GenericOffer.objects.filter(active=True,offerType="WE").count()
    totalChildcareShortterm = GenericOffer.objects.filter(active=True,offerType="BA").count()
    totalChildcareLongterm = GenericOffer.objects.filter(active=True,offerType="CL").count()
    totalJobs = GenericOffer.objects.filter(active=True,offerType="JO").count()
    totalDonations = GenericOffer.objects.filter(active=True,offerType="DO").count()
    context = {
        'city' : city,
        'range': rangeKm,
        'local' : {'PsychologicalOffers': psych,  'DonationOffers': donations, 'AccommodationOffers': accommodations, 'JobOffers': jobs,'WelfareOffers': welfare, 'TransportationOffers': transportations, 'TranslationOffers': translations, 'BuerocraticOffers': buerocratic, "ChildcareOfferShortterm": childcareShortterm,"ChildcareOfferLongterms": childcareLongterm, "ManpowerOffers": manpower},
        'total' : {'DonationOffers': totalDonations, 'AccommodationOffers': totalAccommodations, 'JobOffers': totalJobs, 'WelfareOffers': totalWelfare, 'TransportationOffers': totalTransportations, 'TranslationOffers': totalTranslations, 'BuerocraticOffer': totalBuerocratic, 'ChildcareOfferShortterm': totalChildcareShortterm, 'ChildcareOfferLongterm': totalChildcareLongterm},
    }
    return render(request, 'offers/search.html', context)
def getTranslationImage(request, firstLanguage, secondLanguage):
    # first load flag from file:
    firstData = ""
    secondData = ""
    if firstLanguage == "not":
        firstLanguage = "no-flag"
    if secondLanguage == "not":
        secondLanguage = "no-flag"
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
        accommodations += GenericOffer.objects.filter(active=True,offerType="AC", postCode=postCode).count()
        translations += GenericOffer.objects.filter(active=True,offerType="TL", postCode=postCode).count()
        transportations += GenericOffer.objects.filter(active=True,offerType="TR", postCode=postCode).count()
        accompaniments += GenericOffer.objects.filter(active=True,offerType="AP", postCode=postCode).count()
        buerocratic += GenericOffer.objects.filter(active=True,offerType="BU", postCode=postCode).count()
        childcareShortterm += GenericOffer.objects.filter(active=True,offerType="BA", postCode=postCode).count()
        welfare += GenericOffer.objects.filter(active=True,offerType="WE", postCode=postCode).count()
        jobs += GenericOffer.objects.filter(active=True,offerType="JO", postCode=postCode).count()
    totalAccommodations = GenericOffer.objects.filter(active=True,offerType="AC").count()
    totalTransportations = GenericOffer.objects.filter(active=True,offerType="TR").count()
    totalTranslations = GenericOffer.objects.filter(active=True,offerType="TL").count()
    totalBuerocratic = GenericOffer.objects.filter(active=True,offerType="BU").count()
    totalWelfare = GenericOffer.objects.filter(active=True,offerType="WE").count()
    totalChildcareShortterm = GenericOffer.objects.filter(active=True,offerType="BA").count()
    totalChildcareLongterm = GenericOffer.objects.filter(active=True,offerType="CL").count()
    totalJobs = GenericOffer.objects.filter(active=True,offerType="JO").count()
    context = {
        'local' : {'AccommodationOffers': accommodations, 'JobOffers': jobs,'WelfareOffers': welfare, 'TransportationOffers': transportations, 'TranslationOffers': translations, 'BuerocraticOffers': buerocratic, "ChildcareOfferShortterms": childcareShortterm,"ChildcareOfferLongterms": childcareLongterm},
        'total' : {'AccommodationOffers': totalAccommodations, 'JobOffers': totalJobs, 'WelfareOffers': totalWelfare, 'TransportationOffers': totalTransportations, 'TranslationOffers': totalTranslations, 'BuerocraticOffer': totalBuerocratic, 'ChildcareOfferShortterm': totalChildcareShortterm, 'ChildcareOfferLongterm': totalChildcareLongterm},
    }
    return render(request, 'offers/list.html', context)
def padByRange(locationData, rangeKm):

    locationData["lngMax"] +=kmInLng(rangeKm, locationData["latMax"])
    locationData["latMin"]-=kmInLat(rangeKm)
    locationData["lngMin"]-=kmInLng(rangeKm,  locationData["latMax"])
    locationData["latMax"]+=kmInLat(rangeKm )
    return locationData

def filter(request):
    N_ENTRIES = 5
    filters = {"genericOffer__active": True} 
    if request.POST.get("city"):
        locationData = getCityBbFromLocation(request.POST.get("city"))
        locationData = padByRange(locationData, request.POST.get("range")) #Already padding before...
        filters = {"genericOffer__lat__range": (locationData["latMin"], locationData["latMax"]),"genericOffer__lng__range": (locationData["lngMin"], locationData["lngMax"]) }
    pageCount = int(request.POST.get("page", 0))
    logger.warning(str(filters))
    ids = []
    mapparameter = ""
    currentFilter = dict(request.POST)
    if not currentFilter:
        currentFilter = dict(request.GET)
    categoryCounter = 1
    for key in request.POST:
        if "Visible" in key:
            categoryCounter = categoryCounter +1 
            if "child" in key:
                mapparameter= "childcare"+"=True"
            else:
                mapparameter = key.replace("Visible","")+"=True"
    for key in request.GET:
        if "Visible" in key:
            categoryCounter = categoryCounter +1 
            if "child" in key:
                mapparameter= "childcare"+"=True"
            else:
                mapparameter = key.replace("Visible","")+"=True"
    if not currentFilter and categoryCount == 1:
        categoryCounter = 11
    N_ENTRIES = int(50 / categoryCounter)
    firstEntry = (pageCount+1)* N_ENTRIES
    lastEntry = pageCount * N_ENTRIES
    logger.warning("First : "+str(firstEntry)+" Last: "+str(lastEntry)+" N_ENTRIES"+str(N_ENTRIES)+" Categories: "+str(categoryCounter))
    childShort = ChildCareFilterShortterm(request.POST, queryset=ChildcareOfferShortterm.objects.filter(**filters))
    childShortEntries = mergeImages(childShort.qs[lastEntry:firstEntry])
    
    childLong = ChildCareFilterLongterm(request.POST, queryset=ChildcareOfferLongterm.objects.filter(**filters))
    accommodation = AccommodationFilter(request.POST, queryset=AccommodationOffer.objects.filter(**filters))
    translation = TranslationFilter(request.POST, queryset=TranslationOffer.objects.filter(**filters))
    transportation = TransportationFilter(request.POST, queryset=TransportationOffer.objects.filter(**filters))
    job = JobFilter(request.POST, queryset=JobOffer.objects.filter(**filters))
    buerocratic = BuerocraticFilter(request.POST, queryset=BuerocraticOffer.objects.filter(**filters))
    welfare = WelfareFilter(request.POST, queryset=WelfareOffer.objects.filter(**filters))
    manpower = ManpowerOffer.objects.filter(**filters)
    
    childLongEntries = mergeImages(childLong.qs[lastEntry:firstEntry])
    welfareEntries = mergeImages(welfare.qs[lastEntry:firstEntry])
    maxPage = 0
    numEntries = 0
    context = {'currentFilter': currentFilter, "mapparameter": mapparameter,"ResultCount": 0,"location": request.POST.get("city"), "range": request.POST.get("range"),
    'entries': {},
    'filter': {'childShort' : childShort, 'childLong': childLong, 'accommodation': accommodation, 'translation': translation, 'transportation': transportation, 'job': job, 'buerocratic': buerocratic, 'welfare': welfare}, 'page': pageCount, 'maxPage': maxPage}
    
    if request.POST.get("childShortVisible", "0") == "1" or request.GET.get("childShortVisible") == "True" or not currentFilter :
        numEntries += len(childShort.qs)
        context["entries"]["childShort"] = mergeImages(childShort.qs[lastEntry:firstEntry])
    if request.POST.get("childLongVisible", "0") == "1" or request.GET.get("childLongVisible") == "True"or not currentFilter:
        numEntries += len(childLong.qs)
        context["entries"]["childLong"] = mergeImages(childLong.qs[lastEntry:firstEntry])
    if request.POST.get("jobVisible", "0") == "1" or request.GET.get("jobVisible") == "True" or not currentFilter:
        numEntries += len(job.qs)
        context["entries"]['job'] = mergeImages(job.qs[lastEntry:firstEntry])
    if request.POST.get("buerocraticVisible", "0") == "1"or request.GET.get("buerocraticVisible") == "True" or not currentFilter:
        numEntries += len(buerocratic.qs)
        context["entries"]["buerocratic"] = mergeImages(buerocratic.qs[lastEntry:firstEntry])
    if request.POST.get("welfareVisible", "0") == "1"or request.GET.get("welfareVisible") == "True" or not currentFilter:
        numEntries += len(welfare.qs)
        context["entries"]["welfare"] = mergeImages(welfare.qs[lastEntry:firstEntry])
    if request.POST.get("manpowerVisible", "0") == "1" or request.GET.get("manpowerVisible") == "True" or not currentFilter:
        numEntries += len(manpower)
        context["entries"]["manpower"] = mergeImages(manpower[lastEntry:firstEntry])
    if request.POST.get("transportationVisible", "0") == "1"or request.GET.get("transportationVisible") == "True" or not currentFilter:
        numEntries += len(transportation.qs)
        context["entries"]["transportation"] = mergeImages(transportation.qs[lastEntry:firstEntry])
    if request.POST.get("translationVisible", "0") == "1"or request.GET.get("translationVisible") == "True" or not currentFilter:
        numEntries += len(translation.qs)
        context["entries"]["translation"] = mergeImages(translation.qs[lastEntry:firstEntry])
    if request.POST.get("accommodationVisible", "0") == "1" or request.GET.get("accommodationVisible") == "True"or not currentFilter:
        numEntries += len(accommodation.qs)
        context["entries"]["accommodation"] = mergeImages(accommodation.qs[lastEntry:firstEntry])
    maxPage = int(numEntries/(N_ENTRIES))
    if not currentFilter:
        context["currentFilter"] = {"childShortVisible": "1","childLongVisible": "1","jobVisible": "1","buerocraticVisible": "1","welfareVisible": "1","manpowerVisible": "1","donationVisible": "1","transportationVisible": "1","translationVisible": "1","accommodationVisible": "1"}
    context["maxPage"] = maxPage
    if maxPage > 1:
        context["pagination"] = True
    context["ResultCount"] = numEntries
    logger.warning("Request was: "+str(dict(request.POST)))
    logger.warning("Sending: "+str(context))
    return  context

def handle_filter(request):
    #if request.POST.get("show_list") == "True" or request.GET.get("show_list"):
    context = filter(request)
    return render(request, 'offers/index.html', context)
  
def mergeImages(offers):
    resultOffers = []
    for entry in  offers: 
        images = ImageClass.objects.filter(offerId= entry.genericOffer.id)
        location = {}
        if entry.genericOffer.location == "":
            location = getCityFromCoordinates({"lat":entry.genericOffer.lat, "lng": entry.genericOffer.lng})
            if location.get("city"):
                entry.genericOffer.location =  location["city"]
            else :
                entry.genericOffer.location = "N/A"
            entry.genericOffer.save()  
        location = {"city": entry.genericOffer.location}
        newEntry =  {
            "image" : None,
            "offer" : entry,
            "location": location
        }
        if len(images) > 0:
            newEntry["image"] = images[0].image
        resultOffers.append(newEntry)
    return resultOffers
N_ENTRIES = 25 # Number of Entries that are calculated per category (to reduce load.. )
def index(request):
    context = filter(request)
    
    return render(request, 'offers/index.html', context)
def donations(request):
    donation = DonationOffer.objects.filter(genericOffer__active=True)
    context = {"ResultCount": donation.count(), "DonationOffers": donation }
    return render(request, 'offers/donations.html', context)
@login_required
def delete_offer(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    if user_is_allowed(request, generic.userId.id):
        generic.delete()
        return index(request )
    else :
        return HttpResponse("Wrong User")
@login_required
def selectOfferType(request):
    context= {"entries": []}
    for entry in GenericOffer.OFFER_CHOICES[:-1]:
        context["entries"].append({"longForm": entry[1],"shortForm": entry[0], "svg":  open('static/img/icons/icon_'+entry[0]+'.svg', 'r').read()})
    return render(request, 'offers/selectOfferType.html', context)
def getFormForOfferType(offerType):
    if offerType == "AC":
        return AccommodationForm()
    elif offerType == "TL":
        return TranslationForm()
    elif offerType == "TR":
        return TransportationForm()
    elif offerType == "BU":
        return BuerocraticForm()
    elif offerType == "MP":
        return ManpowerForm()
    elif offerType == "CL":
        return ChildcareFormLongterm()
    elif offerType == "BA":
        return ChildcareFormShortterm()
    elif offerType == "WE":
        return WelfareForm()
    elif offerType == "JO":
        return JobForm()
@login_required
def create(request):
    if request.method == 'POST':
        return update(request, 0, newly_created=True)
    elif request.method == 'GET':
        context = {}
        offerType = request.GET.get("type")
        newOffer = GenericOffer(offerType=offerType)
        context["genericForm"]  = GenericForm(instance=newOffer)
        context["detailForm"] = getFormForOfferType(request.GET.get("type"))
        if request.GET.get("type") == "AC":
            context["imageForm"] = ImageForm()
        return render(request, 'offers/create.html', context)
def save(request):
    # Fill all empty fields with placeholder values ? 
    form = GenericForm(request.POST)
    for entry in form.errors.as_data():
        form[entry] = "-"
    logger.warning(str(form.errors.as_data()))

def update(request, offer_id, newly_created = False):
    form = GenericForm(request.POST)
       # form.image = request.FILES
    if form.is_valid():
        currentForm = form.cleaned_data
        g = updateGenericModel(currentForm, offer_id, request.user.id)
        if request.FILES.get("image") != None:
            counter = 0
            images = request.FILES.getlist('image')
            for image in images:
                counter = counter + 1
                image = ImageClass(image=image, offerId = g)
                image.save()
        if g is not None:
            if currentForm.get("offerType") == "MP": # Special case since we have no particular fields in this type.
                buForm = ManpowerForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateManpowerModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(buForm.errors))
            if currentForm.get("offerType") == "DO": # Special case since we have no particular fields in this type.
                buForm = DonationForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateDonationModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(buForm.errors))
            if currentForm.get("offerType") == "WE": # Special case since we have no particular fields in this type.
                weForm = WelfareForm(request.POST)
                if weForm.is_valid():
                    currentForm = weForm.cleaned_data
                    a = updateWelfareModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(weForm.errors))
            if currentForm.get("offerType") == "JO": # Special case since we have no particular fields in this type.
                joForm = JobForm(request.POST)
                if joForm.is_valid():
                    currentForm = joForm.cleaned_data
                    a = updateJobModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(joForm.errors))
            if currentForm.get("offerType") == "BA": # Special case since we have no particular fields in this type.
                baForm = ChildcareFormShortterm(request.POST)
                if baForm.is_valid():
                    currentForm = baForm.cleaned_data
                    a = updateChildcareShortTermModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(baForm.errors))
            if currentForm.get("offerType") == "CL": # Special case since we have no particular fields in this type.
                clForm = ChildcareFormLongterm(request.POST)
                if clForm.is_valid():
                    currentForm = clForm.cleaned_data
                    a = updateChildcareLongTermModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(clForm.errors))
            if currentForm.get("offerType") == "BU": # Special case since we have no particular fields in this type.
                buForm = BuerocraticForm(request.POST)
                if buForm.is_valid():
                    currentForm = buForm.cleaned_data
                    a = updateBuerocraticModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(buForm.errors))
            elif currentForm.get("offerType") == "AC":
                acForm = AccommodationForm(request.POST)
                if acForm.is_valid():
                    currentForm = acForm.cleaned_data
                    a = updateAccommodationModel(g, currentForm, offer_id)
                    offer_id = a.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(acForm.errors))
            elif currentForm.get("offerType") == "TR":
                trForm = TransportationForm(request.POST)
                if trForm.is_valid():
                    currentForm = trForm.cleaned_data
                    t = updateTransportationModel(g, currentForm, offer_id)
                    offer_id = t.genericOffer.id
                    
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(trForm.errors))
            if currentForm.get("offerType") == "TL":
                tlForm = TranslationForm(request.POST)
                if tlForm.is_valid():
                    currentForm = tlForm.cleaned_data
                    t = updateTranslationModel(g, currentForm,offer_id)
                    
                    offer_id = t.genericOffer.id
                    return detail(request, offer_id, newly_created=newly_created)
                else:
                    return HttpResponse(str(tlForm.errors))
        else:
            return HttpResponse("Wrong User")
    
    else:
        return HttpResponse(str(form.errors))
def getLocationFromOffer(offer):
    reverse_geocode_result = gmaps.reverse_geocode((offer.lat, offer.lng))
    returnVal = {"lat": str(offer.lat), "lng": str(offer.lng)}
    for x in reverse_geocode_result[0]['address_components']:
        if 'country' in x["types"]:
            returnVal["country"] = x["short_name"]
        if 'locality' in x["types"]:
            returnVal["city"] = x["long_name"]
        if 'postal_code' in x["types"]:
            returnVal["plz"] = x["long_name"]
        if 'sublocality_level_1' in x["types"]:
            returnVal["quarter"] = x["long_name"]
        if 'street_number' in x["types"]:
            returnVal["streetnumber"] = x["long_name"]
        if 'route' in x["types"]:
            returnVal["streetname"] = x["long_name"]
    
    returnVal["string"] = reverse_geocode_result[0]["formatted_address"]
    return returnVal


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
    location = getLocationFromOffer(generic)

    if generic.offerType == "AC":
        detail = get_object_or_404(AccommodationOffer, pk=generic.id)
        detailForm = AccommodationForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), 'generic': genericForm, 'detail': detailForm, "location": location, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "WE":
        detail = get_object_or_404(WelfareOffer, pk=generic.id)
        detailForm = WelfareForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), 'generic': genericForm, 'detail': detailForm,"location": location, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TL":
        detail = get_object_or_404(TranslationOffer, pk=generic.id)
        detailForm = TranslationForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(),"location": location,'firstLanguage': detail.firstLanguage.country, 'secondLanguage': detail.secondLanguage.country, 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "TR":
        detail = get_object_or_404(TransportationOffer, pk=generic.id)
        detailForm = TransportationForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), "location": location,'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()}
    if generic.offerType == "MP":
        detail = get_object_or_404(ManpowerOffer, pk=generic.id)
        detailForm = ManpowerForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), "location": location,'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "DO":
        detail = get_object_or_404(DonationOffer, pk=generic.id)
        detailForm = DonationForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), "location": location,'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "BA":
        detail = get_object_or_404(ChildcareOfferShortterm, pk=generic.id)
        detailForm = ChildcareFormShortterm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(),"location": location, 'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "CL":
        detail = get_object_or_404(ChildcareOfferLongterm, pk=generic.id)
        detailForm = ChildcareFormLongterm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), "location": location,'generic': genericForm, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "JO":
        detail = get_object_or_404(JobOffer, pk=generic.id)
        detailForm = JobForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), 'generic': genericForm,"location": location, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 
    if generic.offerType == "BU":
        detail = get_object_or_404(BuerocraticOffer, pk=generic.id)
        detailForm = BuerocraticForm(model_to_dict(detail))
        return {'offerType': generic.get_offerType_display(), 'generic': genericForm,"location": location, 'detail': detailForm, "id": generic.id, "edit_allowed": allowed, "images": images, "imageForm": ImageForm()} 

def detail(request, offer_id, edit_active = False,  newly_created = False) :
    context = getOfferDetails(request, offer_id)
    offer = GenericOffer.objects.get(pk=offer_id)
    logger.warning("created: "+str(offer.created_at))
    context["createdAt"] = offer.created_at.strftime("%d.%m.%Y")
    context["username"] = offer.userId.first_name
    if edit_active:
        context["edit_active"] = edit_active
    if newly_created:
        context["newly_created"] = newly_created
    if request.user.is_authenticated and request.user.isRefugee:
        # If the current user is a Refugee: Check if they have favourited this offer and add it to the recently viewed offers
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

def create_js(request):
    return render(request, 'offers/create_offers.js', {}, content_type='text/javascript')