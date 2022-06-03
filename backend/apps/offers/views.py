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


# Number of offer/request/helpRequest cards to be shown per page by the paginator
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

def padByRange(locationData, rangeKm):
    locationData["lngMax"] +=kmInLng(rangeKm, locationData["latMax"])
    locationData["latMin"]-=kmInLat(rangeKm)
    locationData["lngMin"]-=kmInLng(rangeKm,  locationData["latMax"])
    locationData["latMax"]+=kmInLat(rangeKm )
    return locationData

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