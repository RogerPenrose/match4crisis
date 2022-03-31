
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('list', views.index, name='index'),
    path('by_type/<str:offer_type>', views.by_type, name='by_type'),
    path('search', views.search, name='search'),
    path('by_city/<str:city>', views.by_city, name='by_city'),
    path('create', views.create, name='create'),
    # ex: /polls/5/
    path('<int:offer_id>/', views.detail, name='detail'),
    path('<int:offer_id>/contact', views.contact, name='contact'),
    path('<int:offer_id>/delete_offer', views.delete_offer, name='delete'),
    path('<int:offer_id>/delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('<int:offer_id>/update', views.update, name='update'),
    path('by_postCode/<str:postCode>', views.by_postCode, name='by_postCode')
]