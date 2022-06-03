import re
from tabnanny import check
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse
from django.shortcuts import get_object_or_404,render, redirect
import logging
from os.path import dirname, abspath, join
import json
import googlemaps
from django.conf import settings
import math
import base64
from django.db.models.query import QuerySet
from django.template.loader import get_template
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from apps.accounts.models import User
from django.utils import timezone
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from apps.ineedhelp.models import Refugee
from apps.iamorganisation.models import HelpRequest, Organisation
from apps.iamorganisation.filters import HelpRequestFilter
from .utils import send_manpower_offer_message, send_offer_message
from .filters import OFFER_FILTERS, GenericFilter, AccommodationFilter, TranslationFilter, TransportationFilter, BuerocraticFilter, ManpowerFilter,  ChildcareFilter, WelfareFilter, JobFilter
from .models import OFFER_CARD_NAMES, OFFER_MODELS, GenericOffer, AccommodationOffer, TranslationOffer, TransportationOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOffer, WelfareOffer, JobOffer
from .forms import OFFER_FORMS, AccommodationForm, GenericForm, LocationSearchForm, OfferTypeSearchForm, TransportationForm, TranslationForm, ImageForm, BuerocraticForm, ManpowerForm, ChildcareForm, WelfareForm, JobForm
from django.contrib.auth.decorators import login_required
import re

gmaps = googlemaps.Client(key='AIzaSyAuyDEd4WZh-OrW8f87qmS-0sSrY47Bblk')
# Helper object to map some unfortunate misnamings etc and to massively reduce clutter below.      
logger = logging.getLogger("django")

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
def contact(request, offer_id):
    if request.method == "POST":

        user = request.user
        offer = GenericOffer.objects.get(pk=offer_id)
        recipient = offer.userId

        if user.isOrganisation:
            send_manpower_offer_message(offer, request.POST.get('message'), recipient, Organisation.objects.get(user=user), get_current_site(request).domain)

        else:
            send_offer_message(offer, request.POST.get('message'), recipient, user, get_current_site(request).domain)

            # If the current user is a Refugee add this offer to their recently contacted offers
            if request.user.isRefugee:
                Refugee.objects.get(user=user).addRecentlyContactedOffer(offer)
                
            # TODO helper's recently contacted

        return detail(request, offer_id, contacted = True)
    else:
        details = getOfferDetails(request,offer_id)
        return render(request, 'offers/contact.html', details)
def select_category(request):
    city = ""
    lat = 51.13
    lng = 10.018
    lngMax = 360
    lngMin = -360
    latMax =90
    latMin = -90
    locationData={"latMin": latMin, "lngMin":lngMin, "lngMax":lngMax, "latMax":latMax}
    rangeKm = request.GET.get("range")
    filters ={"active": True, "requestForHelp": False}
    filters_generic = {"genericOffer__active": True, "genericOffer__requestForHelp": False}
    if request.GET.get("requests") == "1":
        filters["requestForHelp"] = True
        filters_generic["genericOffer__requestForHelp"]= True
    logger.warning("Request get: "+str(request.GET.dict()))
    if request.GET.get("location") != "-1":
        if request.GET.get("lat") is not None: 
            bb = json.loads(request.GET.get("bb"))
            locationData = { "city": request.GET.get("location"), "lngMax": bb["east"], "lngMin": bb["west"], "latMax": bb["north"], "latMin": bb["south"]}
            city = locationData["city"]
            locationData = padByRange(locationData,rangeKm)
        elif  request.GET.get("location")  is not None: 
            locationData = getCityBbFromLocation(request.GET.get("location"))
            logger.warning("Getting BB from City?!")
            locationData = padByRange(locationData,rangeKm)
            city = locationData["city"]
        lat = locationData["latMin"]+(locationData["latMax"]-locationData["latMin"])/2
        lng = locationData["lngMin"]+(locationData["lngMax"]-locationData["lngMin"])/2
        filters["lat__range"] = (locationData["latMin"], locationData["latMax"])
        filters["lng__range"] = (locationData["lngMin"], locationData["lngMax"])
        filters_generic["genericOffer__lat__range"] = (locationData["latMin"], locationData["latMax"])
        filters_generic["genericOffer__lng__range"] = (locationData["lngMin"], locationData["lngMax"])
    filters_noLocation = { "active": filters["active"], "requestForHelp": filters["requestForHelp"]}
    #location = getCityBbFromLocation(locationData)
    #Dummy data:
    accommodations = GenericOffer.objects.filter(offerType="AC",**filters).count()
    translations = GenericOffer.objects.filter(offerType="TL",**filters).count()
    transportations = GenericOffer.objects.filter(offerType="TR",**filters).count()
    accompaniments = GenericOffer.objects.filter(offerType="AP",**filters).count()
    buerocratic = GenericOffer.objects.filter(offerType="BU",**filters).count()
    childcare = GenericOffer.objects.filter(offerType="CL",**filters).count()
    welfare = WelfareOffer.objects.filter(helpType__in=["ELD","DIS"], **filters_generic).count()
    psych = WelfareOffer.objects.filter(helpType="PSY",**filters_generic).count()
    jobs = GenericOffer.objects.filter(offerType="JO", **filters).count()
    manpower = GenericOffer.objects.filter(offerType="MP", **filters).count()
    totalAccommodations = GenericOffer.objects.filter(offerType="AC",**filters_noLocation).count()
    totalTransportations = GenericOffer.objects.filter(offerType="TR",**filters_noLocation).count()
    totalTranslations = GenericOffer.objects.filter(offerType="TL",**filters_noLocation).count()
    totalBuerocratic = GenericOffer.objects.filter(offerType="BU",**filters_noLocation).count()
    totalWelfare = GenericOffer.objects.filter(offerType="WE",**filters_noLocation).count()
    totalChildcare= GenericOffer.objects.filter(offerType="CL",**filters_noLocation).count()
    totalJobs = GenericOffer.objects.filter(offerType="JO",**filters_noLocation).count()
    context = {
        'lat' : lat, 'lng': lng,
        'city' : city,
        'range': rangeKm,
        'requestForHelp': filters["requestForHelp"],
        'local' : {'PsychologicalOffers': psych, 'AccommodationOffers': accommodations, 'JobOffers': jobs,'WelfareOffers': welfare, 'TransportationOffers': transportations, 'TranslationOffers': translations, 'BuerocraticOffers': buerocratic, "ChildcareOffer": childcare, "ManpowerOffers": manpower},
        'total' : {'AccommodationOffers': totalAccommodations, 'JobOffers': totalJobs, 'WelfareOffers': totalWelfare, 'TransportationOffers': totalTransportations, 'TranslationOffers': totalTranslations, 'BuerocraticOffer': totalBuerocratic, 'ChildcareOffer': totalChildcare},
    }
    logger.warning(str(context))
    return render(request, 'offers/category_select.html', context)
    
def search(request):
    searchingRequests = request.user.is_authenticated and request.user.isHelper
    if request.method == 'POST':
        locationForm = LocationSearchForm(request.POST)
        selectionForm = OfferTypeSearchForm(request.POST)
        if locationForm.is_valid():
            getParams = {k:v for k,v in locationForm.cleaned_data.items() if v}
            offersOrRequests = 'requests' if searchingRequests else 'offers'
            getParams[offersOrRequests] = 'true'

            if selectionForm.is_valid():
                getParams['selected'] = [offersOrRequests + offerType for offerType, selected in selectionForm.cleaned_data.items() if selected]

            queryString = urlencode(getParams, doseq=True)
            return redirect('/offers/list?' + queryString)
    else:
        locationForm = LocationSearchForm()
        selectionForm = OfferTypeSearchForm()
        context = {
            'locationForm' : locationForm,
            'selectionForm' : selectionForm,
            'searchingRequests' : searchingRequests,
        }
        return render(request, 'offers/search.html', context)

def getTranslationImage(request):
    logger.warning("Received: "+str(request.GET.dict()))
    rawData = []
    for key in request.GET.dict():
        language = "no-flag"
        if request.GET[key] != "not":
            language= request.GET[key]
        fileName = staticfiles_storage.path('img/flags/'+language+".svg")
        with open(fileName, "rb") as fileHandle:
            raw = fileHandle.read()
            rawData.append(base64.b64encode(raw))
    logger.warning("Raw Length: "+str(len(rawData)))
    if len(rawData) == 2:
        context = {"firstLanguage" : rawData[0].decode("utf-8"), "secondLanguage" : rawData[1].decode("utf-8")}
        return render(request, 'offers/2-languages.svg', context=context,content_type="image/svg+xml")
    if len(rawData) == 3:
        logger.warning("Three Languages")
        context = {"firstLanguage" : rawData[0].decode("utf-8"), "secondLanguage" : rawData[1].decode("utf-8"), "thirdLanguage": rawData[2].decode("utf-8")}
        return render(request, 'offers/3-languages.svg', context=context,content_type="image/svg+xml")
    if len(rawData) == 4:
        context = {"firstLanguage" : rawData[0].decode("utf-8"), "secondLanguage" : rawData[1].decode("utf-8"), "thirdLanguage": rawData[2].decode("utf-8"),"fourthLanguage": rawData[3].decode("utf-8")}
        return render(request, 'offers/4-languages.svg', context=context,content_type="image/svg+xml")
def padByRange(locationData, rangeKm):

    locationData["lngMax"] +=kmInLng(rangeKm, locationData["latMax"])
    locationData["latMin"]-=kmInLat(rangeKm)
    locationData["lngMin"]-=kmInLng(rangeKm,  locationData["latMax"])
    locationData["latMax"]+=kmInLat(rangeKm )
    return locationData
def filter_get(request):
    filters = {}
    context = {"entries": {}, "currentFilter": {},"filter": {}}
    pageCount = int(request.POST.get("page", 0))
    currentFilter = request.GET.dict()
    categoryCounter = 0
    maxPage = 0
    numEntries = 0
    mapparameter = ""
    rep = {"Visible": "", "Requests": "", "Offers": ""}
    isRequestForHelp = "Offer"
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    keys = []
    for key in request.GET.dict():
        keys.append(key)
    for key in keys:
        category = pattern.sub(lambda m: rep[re.escape(m.group(0))], key)
        if "Visible" in key and request.GET.get(key, "false") == "true":
            categoryCounter += 1
            mapparameter += key.replace("Visible","")+"=True&"
            logger.warning("Ping")
            if "Requests" in key:
                isRequestForHelp = "Request"
                filters[category] = {"genericOffer__active": True, "genericOffer__requestForHelp": True}
            else:
                if isRequestForHelp == "Request":
                    isRequestForHelp = "Mixed"
                filters[category] = {"genericOffer__active": True, "genericOffer__requestForHelp": False}
    if  categoryCounter == 0:
        categoryCounter = 11
    N_ENTRIES = int(50 / categoryCounter)
    firstEntry = (pageCount+1)* N_ENTRIES
    lastEntry = pageCount * N_ENTRIES
    logger.warning("First : "+str(firstEntry)+" Last:"+str(lastEntry)+" Category: "+str(categoryCounter))
    logger.warning(str(filters))
    for key, value in filters.items():
        if key == "childcare":
            childcare = ChildcareFilter(request.GET, queryset=ChildcareOffer.objects.filter(**value))
            context["entries"]["childcare"] =  mergeImages(childcare.qs[lastEntry:firstEntry])
            context["filter"]["childcare"]  = childcare
            numEntries += len(childcare.qs)
        if key == "accommodation":
            accommodation = AccommodationFilter(request.GET, queryset=AccommodationOffer.objects.filter(**value))
            context["entries"]["accommodation"] =  mergeImages(accommodation.qs[lastEntry:firstEntry])
            context["filter"]["accommodation"]  = accommodation
            numEntries += len(accommodation.qs)
        if key == "translation":
            translation = TranslationFilter(request.GET, queryset=TranslationOffer.objects.filter(**value))
            context["entries"]["translation"] =  mergeImages(translation.qs[lastEntry:firstEntry])
            context["filter"]["translation"]  = translation
            numEntries += len(translation.qs)
        if key == "transportation":
            transportation = TransportationFilter(request.GET, queryset=TransportationOffer.objects.filter(**value))
            context["entries"]["transportation"] =  mergeImages(transportation.qs[lastEntry:firstEntry])
            context["filter"]["transportation"]  = transportation
            numEntries += len(transportation.qs)
        if key == "job":
            job = JobFilter(request.POST, queryset=JobOffer.objects.filter(**value))
            context["entries"]["job"] =  mergeImages(job.qs[lastEntry:firstEntry])
            context["filter"]["job"]  = job
            numEntries += len(job.qs)
        if key == "buerocratic":
            buerocratic = BuerocraticFilter(request.GET, queryset=BuerocraticOffer.objects.filter(**value))
            context["entries"]["buerocratic"] =  mergeImages(buerocratic.qs[lastEntry:firstEntry])
            context["filter"]["buerocratic"]  = buerocratic
            numEntries += len(buerocratic.qs)
        if key == "welfare":
            welfare = WelfareFilter(request.GET, queryset=WelfareOffer.objects.filter(**value))
            context["entries"]["welfare"] =  mergeImages(welfare.qs[lastEntry:firstEntry])
            context["filter"]["welfare"]  = welfare
            numEntries += len(welfare.qs)
        if key == "manpower":
            manpower = ManpowerOffer.objects.filter(**value)
            context["entries"]["manpower"] =  mergeImages(manpower[lastEntry:firstEntry])
            context["filter"]["manpower"]  = manpower
            logger.warning(str(context["entries"]["manpower"]))
            numEntries += len(manpower)
    maxPage = int(numEntries/(N_ENTRIES))
    context["maxPage"] = maxPage
    context["page"] = pageCount
    context["mapparameter"] = mapparameter[:-1]
    if maxPage > 1:
        context["pagination"] = True
    context["requestForHelp"] = isRequestForHelp
    context["ResultCount"] = numEntries
    return context

def filter(request):
    N_ENTRIES = 5
    isRequestForHelp = "Offer"
    filters = {"genericOffer__active": True, "genericOffer__requestForHelp": False} 
    logger.warning("Request: "+str(request.POST.dict()))
    if request.POST.get("requests", "False") == "True":
        filters["genericOffer__requestForHelp"] = True
        isRequestForHelp = "Request"
    if request.POST.get("city"):
        locationData = getCityBbFromLocation(request.POST.get("city"))
        locationData = padByRange(locationData, request.POST.get("range")) #Already padding before...
        filterlocation= {"genericOffer__lat__range": (locationData["latMin"], locationData["latMax"]),"genericOffer__lng__range": (locationData["lngMin"], locationData["lngMax"]) }
        filters.update(filterlocation)
    pageCount = int(request.POST.get("page", 0))
    ids = []
    mapparameter = ""
    currentFilter = request.POST.dict()
    if not currentFilter and (request.user.is_anonymous or not request.user.isOrganisation):
        context= filter_get(request)
    elif request.user.is_anonymous or not request.user.isOrganisation : 
        logger.warning("current Filter: "+str(currentFilter))
        categoryCounter = 1
        for key in request.POST:
            if "Visible" in key:
                categoryCounter = categoryCounter +1 
                suffix = "Offers"
                if filters["genericOffer__requestForHelp"] == True:
                    suffix = "Requests"
                if "child" in key:
                    mapparameter+= "childcare"+suffix+"=True&"
                else:
                    mapparameter += key.replace("Visible","")+suffix+"=True&"
        if not currentFilter and categoryCounter == 1:
            categoryCounter = 11
    
        mapparameter = mapparameter[:-1]
        N_ENTRIES = int(50 / categoryCounter)
        firstEntry = (pageCount+1)* N_ENTRIES
        lastEntry = pageCount * N_ENTRIES
        logger.warning("Have: "+str(filters))
        childcare = ChildcareFilter(request.POST, queryset=ChildcareOffer.objects.filter(**filters))
        accommodation = AccommodationFilter(request.POST, queryset=AccommodationOffer.objects.filter(**filters))
        translation = TranslationFilter(request.POST, queryset=TranslationOffer.objects.filter(**filters))
        transportation = TransportationFilter(request.POST, queryset=TransportationOffer.objects.filter(**filters))
        job = JobFilter(request.POST, queryset=JobOffer.objects.filter(**filters))
        buerocratic = BuerocraticFilter(request.POST, queryset=BuerocraticOffer.objects.filter(**filters))
        welfare = WelfareFilter(request.POST, queryset=WelfareOffer.objects.filter(**filters))
        manpower = ManpowerOffer.objects.filter(**filters)
        
        maxPage = 0
        numEntries = 0
        context = {'currentFilter': currentFilter, "mapparameter": mapparameter,"ResultCount": 0,"location": request.POST.get("city"), "range": request.POST.get("range"),
        'entries': {}, 'requestForHelp': isRequestForHelp,
        'filter': {'childcare' : childcare, 'accommodation': accommodation, 'translation': translation, 'transportation': transportation, 'job': job, 'buerocratic': buerocratic, 'welfare': welfare}, 'page': pageCount, 'maxPage': maxPage}
        
        if request.POST.get("childcareVisible", "0") == "1" or request.GET.get("childcareVisible") == "True" or not currentFilter :
            numEntries += len(childcare.qs)
            context["entries"]["childcare"] = mergeImages(childcare.qs[lastEntry:firstEntry])
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
            context["currentFilter"] = {"childcareVisible": "1","jobVisible": "1","buerocraticVisible": "1","welfareVisible": "1","manpowerVisible": "1","transportationVisible": "1","translationVisible": "1","accommodationVisible": "1"}
        context["maxPage"] = maxPage
        if maxPage > 1:
            context["pagination"] = True
        context["ResultCount"] = numEntries
        logger.warning("Result: "+str(context))
    if not request.user.is_anonymous and request.user.isOrganisation:
        manpower = ManpowerOffer.objects.filter(**filters)
        numEntries = len(manpower)
        N_ENTRIES = int(50 / 1)
        firstEntry = (pageCount+1)* N_ENTRIES
        lastEntry = pageCount * N_ENTRIES
        maxPage = int(numEntries/(N_ENTRIES))
        pageCount = int(request.POST.get("page", 0))
        
        context = {'currentFilter': "", "mapparameter": "","ResultCount": len(manpower),"location": request.POST.get("city"), "range": "",
        'entries': {"manpower": mergeImages(manpower[lastEntry:firstEntry])}, 'requestForHelp': False,
        'filter': {'manpower' : manpower}, 'page': pageCount, 'maxPage': maxPage}
    return  context

def alter_offer_type_selection(request):
    referrerURL = urlparse(request.META["HTTP_REFERER"])
    query = parse_qs(referrerURL.query)
    referrerQueryKeys = list(query.keys())
    prevSelected = query['selected'].copy() if 'selected' in query else []

    for oldSel in prevSelected:
        if oldSel not in request.GET:
            query['selected'].remove(oldSel)
            for k in referrerQueryKeys:
                if k.startswith(oldSel) and k != oldSel:
                    del query[k]

    if request.GET:
        if 'selected' not in query:
            query['selected'] = []
        for newSel in request.GET:
            if newSel not in prevSelected:
                query['selected'].append(newSel)

    # Remove the pagination id if present
    query.pop('page', None)
    
    newQueryString = urlencode(query, doseq=True)
    return redirect(referrerURL._replace(query=newQueryString).geturl())

def alter_url_query(request):
    """Alters the query parameters of the current url by adding/replacing with those sent to this function"""
    referrerURLString = request.META["HTTP_REFERER"]
    referrerURL = urlparse(referrerURLString)
    query = parse_qs(referrerURL.query)
    for k in request.GET:
        entries = request.GET.getlist(k)
        if len(entries) == 1:        
            if entries[0] == '':
                query.pop(k, None)
            else:
                query[k] = entries[0]
        else:
            query[k] = [e for e in entries if e != '']

    newQueryString = urlencode(query, doseq=True)

    return redirect(referrerURL._replace(query=newQueryString).geturl())
  
def mergeImages(offers):
    resultOffers = []
    for entry in  offers: 
        images = ImageClass.objects.filter(offerId= entry.genericOffer.id)
        location = {}
        if entry.genericOffer.location == "" or entry.genericOffer.location == " " :
            if  entry.genericOffer.lat is not None and entry.genericOffer.lng is not None:
                location = getCityFromCoordinates({"lat":entry.genericOffer.lat, "lng": entry.genericOffer.lng})
                if location.get("city"):
                    entry.genericOffer.location =  location["city"]
                else:
                    entry.genericOffer.location = ""
            else:
                entry.genericOffer.location = ""
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

# Number of offer/request cards to be shown per page by the paginator
ENTRIES_PER_PAGE = 20

def index(request):
    """Filters offers/requests for help using the data given in the supplied ```request.GET``` parameters."""

    context = {"filters" : {}}

    getData = request.GET
    offerLabels = dict(GenericOffer.OFFER_CHOICES)
    selected = getData.getlist('selected') or []
    entries = []
    counts = {}

    if "offers" in getData:
        counts["offers"] = {"types" : {}}
        context["filters"]["offers"] = {}
        groupCount = 0
        allSelected = True
        for abbr, offerType in OFFER_MODELS.items():
            if abbr != 'MP':
                isSelected = ('offers' + abbr) in selected
                specOfferCount = offerType.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False).count()
                counts["offers"]["types"][abbr] = {"label" : "{} ({})".format(offerLabels[abbr], specOfferCount), 'selected': isSelected}
                allSelected &= isSelected
                groupCount += specOfferCount
                if isSelected:
                    offers = offerType.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False)
                    curFilter = OFFER_FILTERS[abbr](request.GET, queryset=offers, prefix="offers" + abbr)
                    entries += curFilter.qs
                    context["filters"]["offers"][abbr] = {'filter' : curFilter, 'label' : offerLabels[abbr]}
        counts["offers"]["label"] = "{} ({})".format(_("Angebote"), groupCount) 
        counts["offers"]["allSelected"] = allSelected

    if "requests" in getData:
        counts["requests"] = {"types" : {}}
        context["filters"]["requests"] = {}
        groupCount = 0
        allSelected = True
        for abbr, offerType in OFFER_MODELS.items():
            specOfferCount = offerType.objects.filter(genericOffer__requestForHelp=True, genericOffer__active=True, genericOffer__incomplete=False).count()
            isSelected = ('requests' + abbr) in selected
            counts["requests"]["types"][abbr] = {"label" : "{} ({})".format(offerLabels[abbr], specOfferCount), 'selected': isSelected}
            allSelected &= isSelected
            groupCount += specOfferCount
            if isSelected:
                requests = offerType.objects.filter(genericOffer__requestForHelp=True, genericOffer__active=True, genericOffer__incomplete=False)
                curFilter = OFFER_FILTERS[abbr](request.GET, queryset=requests, prefix="requests" + abbr)
                entries += curFilter.qs
                context["filters"]["requests"][abbr] = {'filter' : curFilter, 'label' : offerLabels[abbr]}
        counts["requests"]["label"] = "{} ({})".format(_("Gesuche"), groupCount) 
        counts["requests"]["allSelected"] = allSelected

    if "manpower" in getData:
        if 'offers' not in counts:
            counts["offers"] = {"types" : {}}
        if 'offers' not in context['filters']:
            context["filters"]["offers"] = {}
        mpOfferCount = ManpowerOffer.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False).count()
        isSelected = 'manpower' in selected or 'offersMP' in selected
        counts["offers"]["types"]['MP'] = {"label" : "{} ({})".format(offerLabels['MP'], mpOfferCount), 'selected': isSelected}
        if isSelected:
            mpOffers = ManpowerOffer.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False)
            mpFilter = ManpowerFilter(request.GET, queryset=mpOffers, prefix='offersMP')
            entries += mpFilter.qs
            context["filters"]["offers"]["MP"] = {'filter' : mpFilter, 'label' : offerLabels['MP']}

    helpRequests = []
    if "helpRequests" in getData:
        isSelected = "helpRequests" in selected
        hrCount = HelpRequest.objects.count()
        counts["helpRequests"] = {"label" : "{} ({})".format(_("Hilfeaufrufe"), hrCount), 'selected': isSelected}
        if isSelected:
            helpRequestsUnfiltered = HelpRequest.objects.all()
            curFilter = HelpRequestFilter(request.GET, queryset=helpRequestsUnfiltered, prefix="helpRequests")
            helpRequests = list(curFilter.qs)
            context["helpRequestsFilter"] = {'filter' : curFilter, 'label' : _("Hilfeaufrufe")}

    if 'bb' in request.GET:
        bb = json.loads(request.GET.get('bb'))
        entries = [e for e in entries if e.genericOffer.lat and e.genericOffer.lng and bb['south'] <= e.genericOffer.lat <= bb['north']  and bb['west']  <= e.genericOffer.lng <= bb['east']]
        helpRequests = [e for e in helpRequests if e.lat and e.lng and bb['south'] <= e.lat <= bb['north']  and bb['west']  <= e.lng <= bb['east']]

    context["counts"] = counts

    context["offercardnames"] = OFFER_CARD_NAMES

    paginator = Paginator([{"offer" : o} for o in entries] + helpRequests, ENTRIES_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj

    return render(request, 'offers/index.html', context)

@login_required
def delete_offer(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    check_user_is_allowed(request, generic.userId.id)
    generic.delete()
    return redirect('login_redirect')

@login_required
def selectOfferType(request):
    if 'type' in request.GET:
        specType = request.GET.get('type')
        specModel = OFFER_MODELS[specType]
        if hasattr(specModel, 'HELP_CHOICES'):
            context= {"subtypes": [], "requestForHelp": False, "offerTypeName" : dict(GenericOffer.OFFER_CHOICES)[specType]}
            for subtypeEntry in specModel.HELP_CHOICES:
                context["subtypes"].append({'longForm' : subtypeEntry[1], 'shortForm' : subtypeEntry[0], 'svg' : open('static/img/icons/icon_%s.svg' % specType, 'r').read()})
            if request.GET.get("rfh", "False") == "True":
                context["requestForHelp"] = True
            return render(request, 'offers/select_offer_subtype.html', context)
        else:
            response = redirect('createOffer')
            response['Location'] += '?%s' % request.GET.urlencode()
            return response
    else:
        context= {"entries": [], "requestForHelp": False}
        for entry in GenericOffer.OFFER_CHOICES:
            context["entries"].append({"longForm": entry[1],"shortForm": entry[0], "svg":  open('static/img/icons/icon_%s.svg' % entry[0], 'r').read()})
        if request.GET.get("rfh", "False") == "True":
            context["requestForHelp"] = True
        return render(request, 'offers/select_offer_type.html', context)

@login_required
def toggle_active(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    check_user_is_allowed(request, generic.userId.id)
    generic.active = not generic.active
    generic.save()
    return redirect('detail', offer_id)

@login_required
def create(request):
    if request.method == 'POST':
        return update(request, newly_created=True)
    elif request.method == 'GET':
        context = {'edit' : False}
        offerType = request.GET.get("type")
        offerSubtype = request.GET.get("subtype")
        context["requestForHelp"] = False
        newOffer = GenericOffer(offerType=offerType)
        newSpecOffer = OFFER_MODELS[offerType]()
        if offerSubtype:
            newSpecOffer.helpType = offerSubtype
        if request.GET.get("rfh", "False") == "True":
            context["requestForHelp"] = True
        context["genericForm"]  = GenericForm(instance=newOffer)
        context["detailForm"] = OFFER_FORMS[offerType](instance=newSpecOffer)
        if offerType == "AC":
            context["imageForm"] = ImageForm()
        return render(request, 'offers/create.html', context)

@login_required
def save(request, offer_id=None):
    """
    Saves the offer in its current state and marks it as incomplete
    """
    if request.method == 'POST':
        if offer_id is None:
            genOffer = GenericOffer(userId = request.user, offerType=request.POST["offerType"])
            if request.user.isRefugee:
                genOffer.requestForHelp = True
            specOffer = OFFER_MODELS[genOffer.offerType](genericOffer = genOffer)
        else:
            genOffer = get_object_or_404(GenericOffer, pk=offer_id)
            check_user_is_allowed(request, genOffer.userId.id)
            specOffer = OFFER_MODELS[genOffer.offerType].objects.get(genericOffer=genOffer)
        genOffer.incomplete=True
        logger.warning(str(model_to_dict(genOffer)))
        genForm = GenericForm(request.POST, instance=genOffer)
        specForm = OFFER_FORMS[request.POST["offerType"]](request.POST, instance=specOffer)
        for field in genForm.fields:
            genForm.fields[field].required = False
        for field in specForm.fields:
            specForm.fields[field].required = False
        genForm.save()
        specForm.save()

        if request.FILES.get("image") != None:
            counter = 0
            images = request.FILES.getlist('image')
            for image in images:
                counter = counter + 1
                image = ImageClass(image=image, offerId = genOffer)
                image.save()

    return redirect("login_redirect")

@login_required
def update(request, offer_id = None, newly_created = False):
    logger.warning("request: "+str(request.POST.dict))
    if offer_id is None:
        genOffer = GenericOffer(userId = request.user, offerType=request.POST["offerType"])
        if request.user.isRefugee:
            genOffer.requestForHelp = True
        specOffer = OFFER_MODELS[genOffer.offerType](genericOffer = genOffer)
    else:
        genOffer = get_object_or_404(GenericOffer, pk=offer_id)
        check_user_is_allowed(request, genOffer.userId.id)
        specOffer = OFFER_MODELS[genOffer.offerType].objects.get(genericOffer = genOffer)
    genOffer.incomplete=False
    genOffer.active=True
    genForm = GenericForm(request.POST, instance=genOffer)
    specForm = OFFER_FORMS[genOffer.offerType](request.POST, instance=specOffer)
    genForm.save()
    specForm.save()

    if request.FILES.get("image") != None:
        counter = 0
        images = request.FILES.getlist('image')
        for image in images:
            counter = counter + 1
            image = ImageClass(image=image, offerId = genOffer)
            image.save()

    request.session['offer_newly_created'] = newly_created
    return HttpResponseRedirect("/offers/%s" % genOffer.id)
    
def getLocationFromOffer(offer):
    if(offer.lat is not None and offer.lng is not None):
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
    return None


def check_user_is_allowed(request, target_id, raise_permission_denied = True):
    user = request.user
    if user.is_superuser:
        logger.warning("User is super user", extra={"request" : request})
        return True
    if user.id == target_id or target_id == 0:
        return True
    if raise_permission_denied:
        raise PermissionDenied
    return False

@login_required
def delete_image(request, offer_id, image_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
    check_user_is_allowed(request, generic.userId.id)
    ImageClass.objects.filter(image_id=image_id).delete()
    return detail(request, offer_id, edit_active=True)

def getOfferDetails(request, offer_id):
    generic = get_object_or_404(GenericOffer, pk=offer_id)
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
    allowed = check_user_is_allowed(request, generic.userId.id, raise_permission_denied = False)
    location = generic.location 
    #location = getLocationFromOffer(generic)
    genericContext = {'offerType': generic.get_offerType_display(), 'generic': generic, 'location': location, 'edit_allowed': allowed, 'images': images, 'imageForm': ImageForm(), "id": generic.id, "requestForHelp": generic.requestForHelp}
    
    specOffer = get_object_or_404(OFFER_MODELS[generic.offerType], genericOffer=generic)
    
    genericContext["detail"] = specOffer
    return genericContext

def detail(request, offer_id, edit_active = False,  newly_created = False, contacted = False) :
    context = getOfferDetails(request, offer_id)
    offer = context['generic']
    # incomplete offers shouldn't have a detail page
    # paused offers' detail pages should be visible only to the creator
    if offer.incomplete:
        raise Http404
    if not offer.active:
        check_user_is_allowed(request, offer.userId.id)
    context["createdAt"] = offer.created_at.strftime("%d.%m.%Y")
    context["username"] = offer.userId.first_name
    logger.warning("context: "+str(offer.requestForHelp))
    if 'offer_newly_created' in request.session:
        newly_created = request.session['offer_newly_created']
        del request.session['offer_newly_created']
    if edit_active:
        context["edit_active"] = edit_active
    if newly_created:
        context["newly_created"] = newly_created
    if contacted:
        context["contacted"] = contacted
    if request.user.is_authenticated and request.user.isRefugee and request.user.id != offer.userId.id:
        # If the current user is a Refugee: Check if they have favourited this offer and add it to the recently viewed offers
        context["favourited"] = offer.favouritedBy.filter(user=request.user)
        refugee = Refugee.objects.get(user=request.user)
        refugee.addRecentlyViewedOffer(offer)
    # The current user is able to contact the offer iff:
    # They are not authenticated or
    # They are a helper and the offer is a request for help or
    # They are a refugee and the offer is not a request for help or
    # They are an organisation and the offer is a manpower offer
    context["contactable"] = not request.user.is_authenticated or (request.user.isHelper and offer.requestForHelp) or (request.user.isRefugee and not offer.requestForHelp) or (request.user.isOrganisation and offer.offerType == "MP")
    return render(request, 'offers/detail.html', context)

@login_required
def edit(request, offer_id):
    genOffer = get_object_or_404(GenericOffer, pk=offer_id)
    check_user_is_allowed(request, genOffer.userId.id)

    if request.method == 'POST':
        return update(request, offer_id, newly_created=True)
    else:
        offerType = genOffer.offerType
        specOffer = OFFER_MODELS[offerType].objects.get(genericOffer=genOffer)

        context = {'edit' : True}
        context["requestForHelp"] = genOffer.requestForHelp
        context["genericForm"]  = GenericForm(instance=genOffer)
        context["detailForm"] = OFFER_FORMS[offerType](instance=specOffer)
        if offerType == "AC" or offerType =="CL":
            context["imageForm"] = ImageForm()
        return render(request, 'offers/create.html', context)

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
