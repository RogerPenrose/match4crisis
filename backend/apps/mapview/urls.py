from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("genericOffers", views.genericOffersJSON, name="genericOffersJSON"),
    path("accommodationOffers", views.accommodationOffersJSON, name="accommodationOffersJSON"),
    path("medicalOffers", views.medicalOffersJSON, name="medicalOffersJSON"),
    path("BuerocraticOffers", views.buerocraticOffersJSON, name="buerocraticOffersJSON"),
    path("ManpowerOffers", views.manpowerOffersJSON, name="manpowerOffersJSON"),
    path("ChildcareOffers", views.childcareOffersJSON, name="childcareOffersJSON"),
    path("jobOffers", views.jobOffersJSON, name="jobOffersJSON"),
    path("translationOffers", views.translationOffersJSON, name="translationOffersJSON"),
    path("transportationOffers", views.transportationOffersJSON, name="transportationOffersJSON"),
    path("mapview/", views.mapviewjs, name="mapview/")

]
 