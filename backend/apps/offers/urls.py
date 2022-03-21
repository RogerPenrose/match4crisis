
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('list', views.index, name='index'),
    path('create_offer', views.create, name='create'),
    # ex: /polls/5/
    path('<int:offer_id>/', views.detail, name='detail'),
    path('<int:offer_id>/update', views.update, name='update')
]