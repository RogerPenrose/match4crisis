import json
import time
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


logger = logging.getLogger("django")
def getCenterOfCity(city):
    current_location = dirname(abspath(__file__))
    with open(join(current_location,"files/cities_to_center.json"), "r") as read_file:
        mappings = json.load(read_file)
        center = mappings.get(city.capitalize())
        if center is not None:
            return center
        else:
            logger.error("NO CENTER FOUND FOR CITY "+city+" Trying for a partial match...")
            for entry in mappings:
                if city.lower() in entry.lower():
                    logger.error("Found a match: "+entry)
                    center = mappings.get(entry)
                    return center
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
    logger.warning("Received Request in Mapview: "+str(request.GET))
    if request.GET.get("city"):
        startPosition = getCenterOfCity(request.GET.get("city"))
        zoom = 10
        logger.warning("Received: "+str(startPosition))
    elif 'lat' in request.GET and 'lng' in request.GET:
        startPosition = [float(request.GET.get("lat")),  float(request.GET.get("lng"))]
        zoom = 10

    context = {
    "startPosition":  startPosition,
    "zoom": zoom,
    "mapbox_token": settings.MAPBOX_TOKEN,
    "get_params": getString,
    }
    context.update(request.GET.dict())
    return render(request, "mapview/map.html", context )

def getJSONData(request):
    if request.method != "GET":
        return HttpResponseNotAllowed
    if "type" not in request.GET:
        return HttpResponseBadRequest
    type = request.GET["type"]

    if type == "helpRequests":
        helpRequests = HelpRequest.objects.all()
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_MP.svg'}
        for hr in helpRequests:
            context = {
                'helpRequest': hr,
            }
            data['entries'].append({
                #'popupContent' : render_to_string("offers/accommodation-card.html", {"entry" : {"offer" : offer}}),
                'popupContent' : render_to_string("mapview/help-request-popup-card.html", context),
                'lat' : hr.lat,
                'lng' : hr.lng,
            })
    elif type == "manpower":
        mpOffers = ManpowerOffer.objects.filter(genericOffer__requestForHelp=False)
    elif type[:-2] == "offers" and len(type) == 8:
        offerType = type[-2:]
        offers = OFFER_MODELS[offerType].objects.filter(genericOffer__requestForHelp=False, genericOffer__active=True, genericOffer__incomplete=False)
        data = {'entries' : [], 'iconSrc': '/static/img/icons/icon_{}.svg'.format(offerType), }
        for offer in offers:
            context = {
                'generic' : offer.genericOffer,
                'detail' : offer
            }
            data['entries'].append({
                #'popupContent' : render_to_string("offers/accommodation-card.html", {"entry" : {"offer" : offer}}),
                'popupContent' : render_to_string("mapview/accommodation-popup-card.html", context),
                'lat' : offer.genericOffer.lat,
                'lng' : offer.genericOffer.lng,
            })
    elif type[:-2] == "requests" and len(type) == 10:
        requestType = type[-2:]
        requests = OFFER_MODELS[requestType].objects.filter(genericOffer__requestForHelp=True)

    return JsonResponse(data, safe=False)

    
def getCountsJSON(request):
    if request.method != "GET":
        return HttpResponseNotAllowed
    getData = request.GET

    offerLabels = dict(GenericOffer.OFFER_CHOICES)
    selected = getData.getlist('selected') or []

    counts = {}
    if "helpRequests" in getData:
        counts["helpRequests"] = {"count": HelpRequest.objects.count(), "label" : '<img src="/static/img/icons/icon_MP.svg">{}'.format(_("Hilfeaufrufe")), 'selected': 'helpRequests' in selected}

    if "manpower" in getData:
        counts["manpower"] = {"count": ManpowerOffer.objects.filter(genericOffer__requestForHelp=False).count(), "label" : '<img src="/static/img/icons/icon_MP.svg">{}'.format(offerLabels['MP']), 'selected': 'manpower' in selected or 'offersMP' in selected}

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
            specOfferCount = offerType.objects.filter(genericOffer__requestForHelp=False).count()
            counts["requests"][abbr] = {"count": specOfferCount, "label" : '<img src="/static/img/icons/icon_{}.svg">{}'.format(abbr,offerLabels[abbr]), 'selected': 'requests{}'.format(abbr) in selected}
            groupCount += specOfferCount
        counts["requests"]["groupCount"] = groupCount


    return JsonResponse(counts)



def accommodationOffersJSON(request):
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = AccommodationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp = False)
    else:
        requests = AccommodationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp = True)
    icon =  "<img src=\"/static/img/icons/icon_AC.svg\">"
    facilities = {
        "type" : "accommodation",
        "legend": icon+str(_("Unterbringungen ")),
        "offers":[{
        "text":  """<div style=\"margin-left: -19px; margin-right:-19px; margin-top:-13px;\">
     </div>
      <h4 class=\"popup-title\">"""+e.genericOffer.offerTitle+"""</h4>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"18\" height=\"18\" fill=\"currentColor\" class=\"bi bi-people\" viewBox=\"0 0 18 18\">
          <path d=\"M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z\"/>
        </svg> 
       """+ str(e.numberOfPeople)+"""  Bewohner | Haustiere:"""+str(_("Ja") if e.petsAllowed else _("Nein"))+"""
      </p>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-calendar\" viewBox=\"0 0 18 18\">
          <path d=\"M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z\"/>
        </svg>"""+str(e.startDateAccommodation)+"""
      </p>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-house\" viewBox=\"0 0 18 18\">
          <path fill-rule=\"evenodd\" d=\"M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z\"/>
          <path fill-rule=\"evenodd\" d=\"M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z\"/>
        </svg> """+e.get_typeOfResidence_display()+"""</p> \n
      <p style=\"padding-top: 5px;\">
        <a href=\"/offers/"""+str(e.genericOffer.id)+"""\" target=\"_blank\" class=\"btn\">Mehr dazu</a>
      </p>""",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in offers],
    "requests":[{
        "text":  """<div style=\"margin-left: -19px; margin-right:-19px; margin-top:-13px;\">
     </div>
      <h4 class=\"popup-title\">"""+e.genericOffer.offerTitle+"""</h4>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"18\" height=\"18\" fill=\"currentColor\" class=\"bi bi-people\" viewBox=\"0 0 18 18\">
          <path d=\"M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z\"/>
        </svg> 
       """+str(e.numberOfPeople)+"""  Bewohner | Haustiere:"""+str(_("Ja") if e.petsAllowed else _("Nein"))+"""
      </p>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-calendar\" viewBox=\"0 0 18 18\">
          <path d=\"M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z\"/>
        </svg>"""+str(e.startDateAccommodation)+"""
      </p>
      <p class=\"icon\">
        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-house\" viewBox=\"0 0 18 18\">
          <path fill-rule=\"evenodd\" d=\"M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z\"/>
          <path fill-rule=\"evenodd\" d=\"M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z\"/>
        </svg> """+e.get_typeOfResidence_display()+"""</p> \n
      <p style=\"padding-top: 5px;\">
        <a href=\"/offers/"""+str(e.genericOffer.id)+"""\" target=\"_blank\" class=\"btn\">Mehr dazu</a>
      </p>""",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) # safe=False is needed to return Arrays
LOCATION_SVG = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-geo-alt\" viewBox=\"0 0 16 16\"> \
  <path d=\"M12.166 8.94c-.524 1.062-1.234 2.12-1.96 3.07A31.493 31.493 0 0 1 8 14.58a31.481 31.481 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304 7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94zM8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10z\"/> \
  <path d=\"M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6z\"/> \
</svg>"    
def transportationOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = TransportationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = TransportationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    
    icon =  "<img src=\"/static/img/icons/icon_TR.svg\">"
    facilities = {
        "type" : "transportation",
        "legend": icon+str(_("Logistik ")),
        "offers":[{
        "text" : "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4> <br>"+LOCATION_SVG+str(e.distance or "N/A")+"km um "+str(e.genericOffer.location or "N/A")+" .\n\n<br>"+str(str(e.numberOfPassengers) if e.helpType == "PT" else "Fahrzeugtyp:"+e.get_typeOfCar_display())+"<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng
    } for e in offers],
    "requests": [{
        "text" : "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4> <br>"+LOCATION_SVG+str(e.distance or "N/A")+"km um "+str(e.genericOffer.location or "N/A")+" .\n\n<br>"+str(str(e.numberOfPassengers) if e.helpType == "PT" else "Fahrzeugtyp:"+e.get_typeOfCar_display())+"<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 
 
def medicalOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = WelfareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = WelfareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    icon =  "<img src=\"/static/img/icons/icon_WE.svg\">"
    facilities = {
        "type" : "welfare",
        "legend": icon+str(_("Medizinische Hilfe ")),
        "offers":[{
        "text": "<h4 class=\"popup-title\">Medizinisches Hilfsangebot</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_helpType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in offers],
    "requests":[{
        "text": "<h4 class=\"popup-title\">Medizinisches Hilfsangebot</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_helpType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 
 
def buerocraticOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = BuerocraticOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = BuerocraticOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    icon =  "<img src=\"/static/img/icons/icon_BU.svg\">"
    facilities = {
        "type" : "buerocracy",
        "legend": icon+str(_("Bürokratische ")),
        "offers":[{
        "text":  "<h4 class=\"popup-title\">Bürokratisches Hilfsangebot</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_helpType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng
    } for e in offers],
    "requests":[{
        "text":  "<h4 class=\"popup-title\">Bürokratisches Hilfsangebot</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_helpType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 


def childcareOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = ChildcareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = ChildcareOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    icon =  "<img src=\"/static/img/icons/icon_CL.svg\">"
    facilities = {
        "type" : "childcare",
        "legend": icon+str(_("Kinderbetreuung ")),
        "offers":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+str("Hat eine Ausbildung\n<br>" if e.hasEducation else "")+str("Hat Erfahrung\n<br>" if e.hasExperience else "")+str("Hat Räumlichkeiten" if e.hasSpace else str(e.distance)+"km Umkreis")+"\n<br>"+e.get_helpType_childcare_display()+"<br>Anzahl Kinder:"+str(e.numberOfChildren)+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in offers],
    "requests":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+str("Hat eine Ausbildung\n<br>" if e.hasEducation else "")+str("Hat Erfahrung\n<br>" if e.hasExperience else "")+str("Hat Räumlichkeiten" if e.hasSpace else str(e.distance)+"km Umkreis")+"\n<br>"+e.get_helpType_childcare_display()+"<br>Anzahl Kinder:"+str(e.numberOfChildren)+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 

def jobOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = JobOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = JobOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    icon =  "<img src=\"/static/img/icons/icon_JO.svg\">"
    facilities = {
        "type" : "joboffers",
        "legend": icon+str(_("Jobangebote ")),
        "offers":[{
        "text":"<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_jobType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in offers],
    "requests":[{
        "text":"<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+e.get_jobType_display()+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 

def manpowerOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee or request.user.isOrganisation:
        offers = ManpowerOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = ManpowerOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    
    icon =  "<img src=\"/static/img/icons/icon_MP.svg\">"
    facilities = {
        "type" : "manpower",
        "legend": icon+str(_("Hilfe vor Ort ")),
        "offers":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>Reisebereitschaft: "+str(e.get_distanceChoices_display())+"\n<br>"+str("Bereit für Auslandseinsätze \n<br>" if e.canGoforeign else"")+str("Hat Krisenerfahrung\n<br>"  if e.hasExperience_crisis else"")+str("Hat medizinische Erfahrung\n<br>" if e.hasMedicalExperience else "")+str("Hat Führerschein" if e.hasDriverslicense else "")+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in offers],
    "requests":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>Reisebereitschaft: "+str(e.get_distanceChoices_display())+"\n<br>"+str("Bereit für Auslandseinsätze \n<br>" if e.canGoforeign else"")+str("Hat Krisenerfahrung\n<br>"  if e.hasExperience_crisis else"")+str("Hat medizinische Erfahrung\n<br>" if e.hasMedicalExperience else "")+str("Hat Führerschein" if e.hasDriverslicense else "")+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.genericOffer.lat,
        "lng": e.genericOffer.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 

def helprequestJSON(request):
    
    requests = HelpRequest.objects.filter()
    logger.warning(str(requests))
    icon =  "<img src=\"/static/img/icons/icon_MP.svg\">"
    facilities = {
        "type" : "request",
        "legend": icon+str(_("Hilfeaufruf ")),
        "offers":[],
    "requests":[{
        "text": "<h4 class=\"popup-title\">"+e.title+"</h4>"+LOCATION_SVG+str(e.location or "N/A")+"\n<br>Beschreibung: "+e.description+"<br><a href=\"/iamorganisation/help_request_detail/"+str(e.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lat": e.lat,
        "lng": e.lng,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 
def translationOffersJSON(request):
    
    requests = []
    offers= []
    if not request.user.is_authenticated or request.user.isRefugee:
        offers = TranslationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=False)
    else:
        requests = TranslationOffer.objects.filter(genericOffer__active = True, genericOffer__isDigital = False, genericOffer__requestForHelp=True)
    icon =  "<img src=\"/static/img/icons/icon_TL.svg\">"
    facilities = {
        "type" : "translation",
        "legend": icon+str(_("Übersetzungen ")),
        "offers":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+str([language.englishName for language in e.languages.all()])+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lng": e.genericOffer.lng,
        "lat": e.genericOffer.lat,
    } for e in offers],"requests":[{
        "text": "<h4 class=\"popup-title\">"+e.genericOffer.offerTitle+"</h4>"+LOCATION_SVG+str(e.genericOffer.location or "N/A")+"\n<br>"+str([language.englishName for language in e.languages.all()])+"\n<br>"+e.genericOffer.offerDescription+"<br><a href=\"/offers/"+str(e.genericOffer.id)+"\" target=\"_blank\">Detailansicht</a>",
        "lng": e.genericOffer.lng,
        "lat": e.genericOffer.lat,
    } for e in requests]}
    return JsonResponse(facilities, safe=False) 


def get_ttl_hash(seconds=300):
    """Return the same value withing `seconds` time period."""
    return round(time.time() / seconds)
