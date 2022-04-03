from django.urls import path

from . import views

urlpatterns = [
    path("thanks", views.thx, name="thanks"),
    path("refugee_dashboard", views.RefugeeDashboardView.as_view(), name="refugee_dashboard"),
    path("favourite_offers", views.favouriteOffers, name="favourite_offers"),

]
