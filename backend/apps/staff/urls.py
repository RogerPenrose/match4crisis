from django.conf import settings
from django.urls import include, path

from . import views

urlpatterns = [
    path("staff_dashboard", views.staff_dashboard, name="staff_dashboard"),
    path("approve_organisations", views.approve_organisations, name="approve_organisations"),
    path(
        "change_organisation_approval/<str:uuid>/",
        views.change_organisation_approval,
        name="change_organisation_approval",
    ),
    path("delete_organisation/<str:uuid>/", views.delete_organisation, name="delete_organisationl"),
]
