from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("AccommodationOffers", views.accommodationOffersJSON, name="accommodationOffersJSON"),
    path("MedicalOffers", views.medicalOffersJSON, name="medicalOffersJSON"),
    path("BuerocraticOffers", views.buerocraticOffersJSON, name="buerocraticOffersJSON"),
    path("ManpowerOffers", views.manpowerOffersJSON, name="manpowerOffersJSON"),
    path("ChildcareOffers", views.childcareOffersJSON, name="childcareOffersJSON"),
    path("generalInformationJSON", views.generalInformationJSON, name="generalInformationJSON"),
    path("JobOffers", views.jobOffersJSON, name="jobOffersJSON"),
    path("TranslationOffers", views.translationOffersJSON, name="translationOffersJSON"),
    path("HelpRequests", views.helprequestJSON, name="helprequestJSON"),
    path("TransportationOffers", views.transportationOffersJSON, name="transportationOffersJSON"),
    path("mapview/", views.mapviewjs, name="mapview/")

]
 