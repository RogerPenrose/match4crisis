from django.urls import path

from . import views

urlpatterns = [
    path("thanks", views.thx, name="thanks"),
    path("helper_dashboard", views.HelperDashboardView.as_view(), name="helper_dashboard"),
]
