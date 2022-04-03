from django.urls import path

from . import views

urlpatterns = [
    path("thanks", views.thx, name="thanks"),
    path("helper_dashboard", views.HelperDashboardView.as_view(), name="helper_dashboard"),
    path("choose_help", views.choose_help, name="choose_help"),
    path("running_offers", views.running_offers, name="running_offers"),
    path("incomplete_offers", views.incomplete_offers, name="incomplete_offers"),
    path("paused_offers", views.paused_offers, name="paused_offers"),
]
