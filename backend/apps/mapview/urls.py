from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("genericOffers", views.genericOffersJSON, name="genericOffersJSON"),
    path("accommodationOffers", views.accommodationOffersJSON, name="accommodationOffersJSON"),
    path("translationOffers", views.translationOffersJSON, name="translationOffersJSON"),
    path("transportationOffers", views.transportationOffersJSON, name="transportationOffersJSON"),
    path("mapview/", views.mapviewjs, name="mapview/")

]
 