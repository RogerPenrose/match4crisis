from django.urls import path

from . import views
urlpatterns = [
    path("refugee_dashboard", views.RefugeeDashboardView.as_view(), name="refugee_dashboard"),
    path("favourite_offers", views.favouriteOffers, name="favourite_offers"),
    path("running_requests", views.running_requests, name="running_requests"),
    path("paused_requests", views.paused_requests, name="paused_requests"),
    path("incomplete_requests", views.incomplete_requests, name="incomplete_requests"),
    path("recently_viewed", views.recentlyViewedOffers, name="recently_viewed"),
    path("recently_contacted", views.recentlyContactedOffers, name="recently_contacted"),
]
