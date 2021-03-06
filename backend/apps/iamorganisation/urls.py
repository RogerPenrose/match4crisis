from django.urls import path, register_converter

from . import views

urlpatterns = [
    path("organisation_dashboard", views.OrganisationDashboardView.as_view(), name="organisation_dashboard"),
    path("request_help", views.request_help, name="request_help"),
    path("help_requests_created", views.help_requests_created, name="help_requests_created"),
    path("request_donations", views.request_donations, name="request_donations"),
    path("create_donation_request", views.create_donation_request, name="create_donation_request"),
    path("create_material_donation_request", views.create_material_donation_request, name="create_material_donation_request"),
    path("organisation_overview", views.OrganisationOverview.as_view(), name="organisation_overview"),
    path("donation_requests", views.donation_overview, name="donation_requests"),
    path("donation_request_created", views.donation_request_created, name="donation_request_created"),
    path("donation_detail/<donation_request_id>/", views.donation_detail, name="donation_detail"),
    path("donation_detail/<donation_request_id>/edit", views.edit_redirect, name="edit_donation_request"),
    path("donation_detail/<donation_request_id>/delete", views.delete_donation_request, name="delete_donation_request"),
    path("donation_detail/<request_id>/toggle_active", views.toggle_active, name="toggle_active_donation_request"),
    path("help_request_detail/<help_request_id>/", views.help_request_detail, name="help_request_detail"),
    path("help_request_detail/<help_request_id>/contact", views.contact_help_request, name="contact_help_request"),
    path("help_request_detail/<help_request_id>/edit", views.edit_help_request, name="edit_help_request"),
    path("help_request_detail/<help_request_id>/delete", views.delete_help_request, name="delete_help_request"),
    path("help_request_detail/<request_id>/toggle_active", views.toggle_active, name="toggle_active_help_request"),
]
