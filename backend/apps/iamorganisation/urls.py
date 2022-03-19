from django.urls import path, register_converter

from . import converters, views

register_converter(converters.DecimalPointFloatConverter, "float")


urlpatterns = [
    path("hospitals/<countrycode>/<plz>", views.hospital_list, name="hospital_list"),
    path("hospital_map", views.hospital_overview, name="hopsital_map"),
    path("change_posting", views.change_posting, name="change_posting"),
]
