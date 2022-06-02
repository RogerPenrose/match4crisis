import logging
import json
from django.shortcuts import render
from os.path import dirname, abspath, join
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.gzip import gzip_page
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string  

from apps.iamorganisation.models import HelpRequest

from apps.offers.models import *
from apps.offers.filters import OFFER_FILTERS, ManpowerFilter


POPUP_CARDS = {
    'AC' : 'accommodation-popup-card.html',
    'TL' : 'translation-popup-card.html',
    'TR' : 'transportation-popup-card.html',
    'BU' : 'buerocratic-popup-card.html',
    'MP' : 'manpower-popup-card.html',
    'CL' : 'childcare-popup-card.html',
    'WE' : 'welfare-popup-card.html',
    'JO' : 'job-popup-card.html',
}

logger = logging.getLogger("django")

def mapviewjs(request):
    context = {}
    context["show"] = []
    BASE= "/mapview/"
    logger.warning(str(request.GET.dict()))
    if not request.user.is_authenticated or not request.user.isOrganisation :
        if request.GET.get("show_mp", ""):
            context["categories"] = [BASE+"HelpRequests"]
        else:
            context["categories"] = [BASE+"AccommodationOffers",  BASE+"BuerocraticOffers", BASE+"ChildcareOffers", BASE+"JobOffers", BASE+"MedicalOffers", BASE+"TransportationOffers", BASE+"TranslationOffers"]
    else:
        #get only MP
        context["categories"] = [BASE+"ManpowerOffers"]
    for key,value in request.GET.dict().items():
        if value == "True" and key != "show_mp":
            context["show"].append(key.replace("Offers","").replace("Requests", ""))
    logger.warning(str(request.GET.dict()))
    logger.warning("rendering mapview JS ? "+str(context))
    return render(request, 'mapview/mapview.js', context , content_type='text/javascript')

# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def index(request):
    startPosition =  [51.13, 10.018]
    zoom = 6
    getString = request.GET.urlencode()
    if 'lat' in request.GET and 'lng' in request.GET:
        startPosition = [float(request.GET.get("lat")),  float(request.GET.get("lng"))]
        zoom = 10

    # create all filters without data (for display)
    context = {'filters' : {}}
    offerLabels = dict(GenericOffer.OFFER_CHOICES)
    if 'offers' in request.GET:
        context['filters']['offers'] = {}
        for abbr in OFFER_MODELS:
            offerFilter = OFFER_FILTERS[abbr](request.GET, prefix="offers"+abbr)
            context["filters"]["offers"][abbr] = {'filter' : offerFilter, 'label' : offerLabels[abbr]}

    if 'requests' in request.GET:
        context['filters']['requests'] = {}
        for abbr in OFFER_MODELS:
            requestFilter = OFFER_FILTERS[abbr](request.GET, prefix="requests"+abbr)
            context["filters"]["requests"][abbr] = {'filter' : requestFilter, 'label' : offerLabels[abbr]}

    context.update({
    "startPosition":  startPosition,
    "zoom": zoom,
    "mapbox_token": settings.MAPBOX_TOKEN,
    "filterTitle": _("Hilfsgesuche filtern") if 'requests' in request.GET else _("Angebote filtern")
    })
    
    return render(request, "mapview/map.html", context )

def getJSONData(request):
    if request.method != "GET":
        return HttpResponseNotAllowed()
    if "type" not in request.GET:
        return HttpResponseBadRequest()
    type = request.GET["type"]

    if type == "helpRequests":
        helpRequests = HelpRequest.objects.all()
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_MP.svg'}
        for hr in helpRequests:
            context = {
                'helpRequest': hr,
            }
            data['entries'].append({
                'popupContent' : render_to_string("mapview/help-request-popup-card.html", context),
                'lat' : hr.lat,
                'lng' : hr.lng,
            })

    elif type == "manpower":
        mpOffers = ManpowerOffer.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False)
        mpFilter = ManpowerFilter(request.GET, queryset=mpOffers, prefix="offersMP")
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_MP.svg', }
        for offer in mpFilter.qs:
            context = {
                'generic' : offer.genericOffer,
                'detail' : offer
            }
            data['entries'].append({
                'popupContent' : render_to_string("mapview/" + POPUP_CARDS['MP'], context),
                'lat' : offer.genericOffer.lat,
                'lng' : offer.genericOffer.lng,
            })

    elif type[:-2] == "offers" and len(type) == 8:
        offerType = type[-2:]
        offers = OFFER_MODELS[offerType].objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False)
        curFilter = OFFER_FILTERS[offerType](request.GET, queryset=offers, prefix="offers"+offerType)
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_{}.svg'.format(offerType), }
        for offer in curFilter.qs:
            context = {
                'generic' : offer.genericOffer,
                'detail' : offer
            }
            data['entries'].append({
                'popupContent' : render_to_string("mapview/" + POPUP_CARDS[offerType], context),
                'lat' : offer.genericOffer.lat,
                'lng' : offer.genericOffer.lng,
            })

    elif type[:-2] == "requests" and len(type) == 10:
        requestType = type[-2:]
        requests = OFFER_MODELS[requestType].objects.filter(genericOffer__requestForHelp=True, genericOffer__active=True, genericOffer__incomplete=False)
        curFilter = OFFER_FILTERS[requestType](request.GET, queryset=requests, prefix="requests"+requestType)
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_{}.svg'.format(requestType), }
        for request in curFilter.qs:
            context = {
                'generic' : request.genericOffer,
                'detail' : request
            }
            data['entries'].append({
                'popupContent' : render_to_string("mapview/" + POPUP_CARDS[requestType], context),
                'lat' : request.genericOffer.lat,
                'lng' : request.genericOffer.lng,
            })
    else:
        data = {}

    return JsonResponse(data, safe=False)

    
def getCountsJSON(request):
    if request.method != "GET":
        return HttpResponseNotAllowed()
    getData = request.GET

    offerLabels = dict(GenericOffer.OFFER_CHOICES)
    selected = getData.getlist('selected') or []

    counts = {}
    if "helpRequests" in getData:
        counts["helpRequests"] = {"count": HelpRequest.objects.count(), "label" : '<img src="/static/img/icons/icon_MP.svg">{}'.format(_("Hilfeaufrufe")), 'selected': 'helpRequests' in selected}

    if "offers" in getData:
        counts["offers"] = {"label" : _("Angebote")}
        groupCount = 0
        for abbr, offerType in OFFER_MODELS.items():
            if abbr != 'MP':
                specOfferCount = offerType.objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False).count()
                counts["offers"][abbr] = {"count": specOfferCount, "label" : '<img src="/static/img/icons/icon_{}.svg">{}'.format(abbr,offerLabels[abbr]), 'selected': 'offers{}'.format(abbr) in selected}
                groupCount += specOfferCount
        counts["offers"]["groupCount"] = groupCount

    if "requests" in getData:
        counts["requests"] = {"label" : _("Gesuche")}
        groupCount = 0
        for abbr, offerType in OFFER_MODELS.items():
            specOfferCount = offerType.objects.filter(genericOffer__requestForHelp=True, genericOffer__active=True, genericOffer__incomplete=False).count()
            counts["requests"][abbr] = {"count": specOfferCount, "label" : '<img src="/static/img/icons/icon_{}.svg">{}'.format(abbr,offerLabels[abbr]), 'selected': 'requests{}'.format(abbr) in selected}
            groupCount += specOfferCount
        counts["requests"]["groupCount"] = groupCount

    if "manpower" in getData:
        counts["offersMP"] = {"count": ManpowerOffer.objects.filter(genericOffer__active=True, genericOffer__incomplete=False, genericOffer__requestForHelp=False).count(), "label" : '<img src="/static/img/icons/icon_MP.svg">{}'.format(offerLabels['MP']), 'selected': 'manpower' in selected or 'offersMP' in selected}

    return JsonResponse(counts)

