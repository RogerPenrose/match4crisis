from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="mapview-index"),
    path("AccommodationOffers", views.accommodationOffersJSON, name="accommodationOffersJSON"),
    path("MedicalOffers", views.medicalOffersJSON, name="medicalOffersJSON"),
    path("BuerocraticOffers", views.buerocraticOffersJSON, name="buerocraticOffersJSON"),
    path("ManpowerOffers", views.manpowerOffersJSON, name="manpowerOffersJSON"),
    path("ChildcareOffers", views.childcareOffersJSON, name="childcareOffersJSON"),
    path("JobOffers", views.jobOffersJSON, name="jobOffersJSON"),
    path("TranslationOffers", views.translationOffersJSON, name="translationOffersJSON"),
    path("HelpRequests", views.helprequestJSON, name="helprequestJSON"),
    path("TransportationOffers", views.transportationOffersJSON, name="transportationOffersJSON"),
    path("mapview/", views.mapviewjs, name="mapview/"),
    path("counts", views.getCountsJSON, name="getCountsJSON"),
    path("data", views.getJSONData, name="getJSONData")

]
 