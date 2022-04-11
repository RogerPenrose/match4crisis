from django.conf import settings
from django.urls import include, path

from . import views

urlpatterns = [
    path("staff_dashboard", views.staff_dashboard, name="staff_dashboard"),
    path("approve_organisations", views.approve_organisations, name="approve_organisations"),
    path(
        "change_organisation_approval/<str:id>/",
        views.change_organisation_approval,
        name="change_organisation_approval",
    ),
    path("delete_organisation/<str:uuid>/", views.delete_organisation, name="delete_organisationl"),
    path("view_newsletter/<id>", views.view_newsletter, name="view_newsletter"),
    path("new_newsletter", views.new_newsletter, name="new_newsletter"),
    path("list_newsletter", views.list_newsletter, name="list_newsletter"),
    path("did_see_newsletter/<id>/<token>", views.did_see_newsletter, name="did_see_newsletter"),
    path("database_stats", views.database_stats, name="database_stats"),
    path("confirm_delete/<str:uuid>", views.confirm_delete, name="confirm_delete"),
]
