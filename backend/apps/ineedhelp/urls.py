from django.urls import path

from . import views

urlpatterns = [
    path("thanks", views.thx, name="thanks"),
    path("refugee_dashboard", views.RefugeeDashboardView.as_view(), name="refugee_dashboard"),
    path("favourite_offers", views.favouriteOffers, name="favourite_offers"),
    path("recently_viewed", views.recentlyViewedOffers, name="recently_viewed"),
    path("recently_contacted", views.recentlyContactedOffers, name="recently_contacted"),
]
