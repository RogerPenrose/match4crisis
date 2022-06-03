from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="mapview-index"),
    path("counts", views.getCountsJSON, name="getCountsJSON"),
    path("data", views.getJSONData, name="getJSONData")
]
 