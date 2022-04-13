
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('list', views.index, name='index'),
    path('handle_filter', views.handle_filter, name="filter"),
    path('search', views.search, name='search'),
    path('by_city/<str:city>', views.by_city, name='by_city'),
    path('createOffer', views.create, name='create'),
    path('create', views.selectOfferType, name='create'),
    path('save', views.save, name='save'),
    path('donations', views.donations, name="donations"),
    # ex: /polls/5/
    path('<int:offer_id>/', views.detail, name='detail'),
    path('<int:offer_id>/contact', views.contact, name='contact'),
    path('translation/<str:firstLanguage>_<str:secondLanguage>', views.getTranslationImage, name="image"),
    path('<int:offer_id>/delete_offer', views.delete_offer, name='delete'),
    path('<int:offer_id>/delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('<int:offer_id>/update', views.update, name='update'),
    path('ajax_toggle_favourite', views.ajax_toggle_favourite, name='ajax_toggle_favourite'),

    path("create_js/", views.create_js, name='create_js'),
]