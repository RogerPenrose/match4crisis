
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('create', views.create, name='create'),
    # ex: /polls/5/
    path('<int:offer_id>/', views.detail, name='detail')
]