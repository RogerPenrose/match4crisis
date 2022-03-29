from django.urls import path, register_converter

from . import converters, views

register_converter(converters.DecimalPointFloatConverter, "float")


urlpatterns = [
    path("organisations/<countrycode>/<plz>", views.organisation_list, name="organisation_list"),
    path("organisation_map", views.organisation_overview, name="hopsital_map"),
    path("change_posting", views.change_posting, name="change_posting"),
    path("thanks_organisation", views.thx, name="thanks_organisation"),
    path("organisation_dashboard", views.OrganisationDashboardView.as_view(), name="organisation_dashboard"),
]
