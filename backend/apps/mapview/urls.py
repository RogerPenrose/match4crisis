from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("genericOffers", views.genericOffersJSON, name="genericOffersJSON"),
    path("accomodationOffers", views.accomodationOffersJSON, name="accomodationOffersJSON"),
    path("translationOffers", views.translationOffersJSON, name="translationOffersJSON"),
    path("transportationOffers", views.transportationOffersJSON, name="transportationOffersJSON")
]
