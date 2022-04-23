from django.urls import path, register_converter

from . import converters, views

register_converter(converters.DecimalPointFloatConverter, "float")


urlpatterns = [
    path("organisations/<countrycode>/<plz>", views.organisation_list, name="organisation_list"),
    path("organisation_map", views.organisation_overview, name="hopsital_map"),
    path("thanks_organisation", views.thx, name="thanks_organisation"),
    path("organisation_dashboard", views.OrganisationDashboardView.as_view(), name="organisation_dashboard"),
    path("request_help", views.request_help, name="request_help"),
    path("request_donations", views.create_donation_request, name="request_donations"),
    path("sent_requests", views.sent_requests, name="sent_requests"),
    #path("organisation_view/<str:uuid>/", views.organisation_view, name="organisation_view"),
    path("organisation_overview", views.organisation_overview, name="organisation_overview"),
    path("donation_detail/<donation_request_id>", views.donation_detail, name="donation_detail"),
]
