
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('list', views.index, name='index'),
    path('create', views.create, name='create'),
    # ex: /polls/5/
    path('<int:offer_id>/', views.detail, name='detail'),
    path('<int:offer_id>/update', views.update, name='update'),
    path('by_postCode/<str:postCode>', views.by_postCode, name='by_postCode')
]