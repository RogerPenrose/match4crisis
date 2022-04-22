import re
from django.shortcuts import get_object_or_404,render, redirect
import logging
from os.path import dirname, abspath, join
import json
import googlemaps
from django.conf import settings
import math
import base64
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from apps.accounts.models import User
from django.utils import timezone
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from apps.ineedhelp.models import Refugee
from apps.accounts.decorator import helperRequired, refugeeRequired
from .filters import GenericFilter, AccommodationFilter, TranslationFilter, TransportationFilter, BuerocraticFilter, ManpowerFilter,  ChildCareFilterLongterm, ChildCareFilterShortterm, WelfareFilter, JobFilter
from .models import OFFER_MODELS, GenericOffer, AccommodationOffer, TranslationOffer, TransportationOffer, ImageClass, BuerocraticOffer, ManpowerOffer, ChildcareOfferLongterm, ChildcareOfferShortterm, WelfareOffer, JobOffer, DonationOffer
from .forms import OFFER_FORMS, AccommodationForm, GenericForm, TransportationForm, TranslationForm, ImageForm, BuerocraticForm, ManpowerForm, ChildcareFormLongterm, ChildcareFormShortterm, WelfareForm, JobForm, DonationForm
from django.contrib.auth.decorators import login_required

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
@refugeeRequired
def contact(request, offer_id):
    if request.method == "POST":
        # TODO send email

        # If the current user is a Refugee: Add this offer to their recently contacted offers
        if request.user.is_authenticated and request.user.isRefugee:
            subject = _("Anfrage zu deinem Hilfsangebot")
            
            message = request.POST.get("message")
            plaintext = get_template('offers/contact_email.txt')
            htmly     = get_template('offers/contact_email.html')
            contactData = _("E-Mail : ")+request.user.email+ " "
            if request.user.sharePhoneNumber and request.user.phoneNumber is not None:
                contactData += _("Telefon : ")+request.user.phoneNumber
            recipientUser = GenericOffer.objects.get(pk=offer_id).userId
            recipient = recipientUser.email
            logger.warning("Trying to send: "+message+" To: "+recipient)
            d = { "message": message, "contact": contactData,'sender': request.user.first_name+" "+request.user.last_name, 'recipient': recipientUser.first_name, 'message':message, "link":"http://match4crisis.org/offers/"+str(offer_id)+"/"}
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            send_mail(subject, message,
                      settings.DEFAULT_FROM_EMAIL, [recipient], html_message=html_content)
            offer = GenericOffer.objects.get(pk=offer_id)
            refugee = Refugee.objects.get(user=request.user)
            refugee.addRecentlyContactedOffer(offer)
        return detail(request, offer_id, contacted = True)
    else:
        details = getOfferDetails(request,offer_id)
        return render(request, 'offers/contact.html', details)
def select_category(request):
    city = ""
    lngMax = 360
    lngMin = -360
    latMax =90
    latMin = -90
    locationData={"latMin": latMin, "lngMin":lngMin, "lngMax":lngMax, "latMax":latMax}
    rangeKm = request.GET.get("range")
    filters ={"active": True}
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
        
        filters["lat__range"] = (locationData["latMin"], locationData["latMax"])
        filters["lng__range"] = (locationData["lngMin"], locationData["lngMax"])

    #location = getCityBbFromLocation(locationData)
    #Dummy data:
    accommodations = GenericOffer.objects.filter(offerType="AC",**filters).count()
    translations = GenericOffer.objects.filter(offerType="TL",**filters).count()
    transportations = GenericOffer.objects.filter(offerType="TR",**filters).count()
    accompaniments = GenericOffer.objects.filter(offerType="AP",**filters).count()
    buerocratic = GenericOffer.objects.filter(offerType="BU",**filters).count()
    childcareShortterm = GenericOffer.objects.filter(offerType="BA",**filters).count()
    welfare = WelfareOffer.objects.filter(genericOffer__active=True,helpType_welfare__in=["ELD","DIS"], genericOffer__lat__range=(locationData["latMin"], locationData["latMax"]), genericOffer__lng__range=(locationData["lngMin"], locationData["lngMax"])).count()
    psych = WelfareOffer.objects.filter(genericOffer__active=True,helpType_welfare="PSY", genericOffer__lat__range=(locationData["latMin"], locationData["latMax"]), genericOffer__lng__range=(locationData["lngMin"], locationData["lngMax"])).count()
    jobs = GenericOffer.objects.filter(offerType="JO", **filters).count()
    childcareLongterm = GenericOffer.objects.filter(offerType="CL", **filters).count()
    manpower = GenericOffer.objects.filter(offerType="MP", **filters).count()
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
    logger.warning(str(context))
    return render(request, 'offers/category_select.html', context)
    
def search(request):
    # Ideally: Associate Postcode with city here...
    #Get list of all PostCodes within the City: 
    return render(request, 'offers/search.html')
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
        filters = {"genericOffer__active": "True", "genericOffer__lat__range": (locationData["latMin"], locationData["latMax"]),"genericOffer__lng__range": (locationData["lngMin"], locationData["lngMax"]) }
    pageCount = int(request.POST.get("page", 0))
    ids = []
    mapparameter = ""
    currentFilter = request.POST.dict()
    if not currentFilter:
        currentFilter = request.GET.dict()
    logger.warning("current Filter: "+str(currentFilter))
    categoryCounter = 1
    for key in request.POST:
        if "Visible" in key:
            categoryCounter = categoryCounter +1 
            if "child" in key:
                mapparameter+= "childcare"+"=True&"
            else:
                mapparameter += key.replace("Visible","")+"=True&"
    for key in request.GET:
        if "city" not in key:
            categoryCounter = categoryCounter +1 
            if "child" in key:
                mapparameter+= "childcare"+"=True&"
            else:
                mapparameter += key.replace("Visible","")+"=True&"
    if not currentFilter and categoryCount == 1:
        categoryCounter = 11
    mapparameter = mapparameter[:-1]
    N_ENTRIES = int(50 / categoryCounter)
    firstEntry = (pageCount+1)* N_ENTRIES
    lastEntry = pageCount * N_ENTRIES
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


@login_required
@helperRequired
def create(request):
    if request.method == 'POST':
        return update(request, newly_created=True)
    elif request.method == 'GET':
        context = {}
        offerType = request.GET.get("type")
        newOffer = GenericOffer(offerType=offerType)
        context["genericForm"]  = GenericForm(instance=newOffer)
        context["detailForm"] = OFFER_FORMS[request.GET.get("type")]()
        if request.GET.get("type") == "AC":
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
            specOffer = OFFER_MODELS[genOffer.offerType](genericOffer = genOffer)
        else:
            genOffer = GenericOffer.objects.get(id=offer_id)
            if(not user_is_allowed(request, genOffer.userId.id)):
                return HttpResponseForbidden("You're not allowed to edit other users' offers.")
            specOffer = OFFER_MODELS[genOffer.offerType].objects.get(genericOffer=genOffer)
        genOffer.incomplete=True
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

    return HttpResponseRedirect("/iofferhelp/helper_dashboard")

@login_required
def update(request, offer_id = None, newly_created = False):
    if offer_id is None:
        genOffer = GenericOffer(userId = request.user, offerType=request.POST["offerType"])
        specOffer = OFFER_MODELS[genOffer.offerType](genericOffer = genOffer)
    else:
        genOffer = GenericOffer.objects.get(pk=offer_id)
        if(not user_is_allowed(request, genOffer.userId.id)):
            return HttpResponseForbidden("You're not allowed to edit other users' entries.")
        specOffer = OFFER_MODELS[genOffer.offerType](genericOffer = genOffer)
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


def user_is_allowed(request, target_id):
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        user = None
    allowed = False
    if user is not None:
        if request.user.id == target_id or user.is_superuser or target_id == 0:
            allowed = True
            if(user.is_superuser):
                logger.warning("User is super user: "+str(user.is_superuser))
        else: 
            return allowed
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

def detail(request, offer_id, edit_active = False,  newly_created = False, contacted = False) :
    context = getOfferDetails(request, offer_id)
    offer = GenericOffer.objects.get(pk=offer_id)
    context["createdAt"] = offer.created_at.strftime("%d.%m.%Y")
    context["username"] = offer.userId.first_name

    if 'offer_newly_created' in request.session:
        newly_created = request.session['offer_newly_created']
        del request.session['offer_newly_created']
    if edit_active:
        context["edit_active"] = edit_active
    if newly_created:
        context["newly_created"] = newly_created
    if contacted:
        context["contacted"] = contacted
    if request.user.is_authenticated and request.user.isRefugee:
        # If the current user is a Refugee: Check if they have favourited this offer and add it to the recently viewed offers
        context["favourited"] = offer.favouritedBy.filter(user=request.user)
        refugee = Refugee.objects.get(user=request.user)
        refugee.addRecentlyViewedOffer(offer)
    return render(request, 'offers/detail.html', context)

def edit(request, offer_id):
    if request.method == 'POST':
        return update(request, offer_id, newly_created=True)
    else:
        genOffer = GenericOffer.objects.get(id=offer_id)
        offerType = genOffer.offerType
        specOffer = OFFER_MODELS[offerType](genericOffer=genOffer)

        context = {}
        context["genericForm"]  = GenericForm(instance=genOffer)
        context["detailForm"] = OFFER_FORMS[offerType](instance=specOffer)
        if offerType == "AC":
            context["imageForm"] = ImageForm()
        return render(request, 'offers/create.html', context)
    #return detail(request, offer_id, edit_active=True)

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