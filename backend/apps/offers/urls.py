
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('list', views.index, name='offers-index'),
    path('select_category', views.select_category, name='select_category'),
    path('handle_filter', views.handle_filter, name="filter"),
    path('apply_filter', views.apply_filter, name="apply_filter"),
    path('search/', views.search, name='search'),
    path('search_requests/', views.search, name='search_requests'),
    path('createOffer', views.create, name='createOffer'),
    path('create', views.selectOfferType, name='create'),
    path('save', views.save, name='save'),
    path('<int:offer_id>/save', views.save, name='save'),
    path('<int:offer_id>/', views.detail, name='detail'),
    path('<int:offer_id>/contact', views.contact, name='contact'),
    path('translation/', views.getTranslationImage, name="image"),
    path('<int:offer_id>/delete_offer', views.delete_offer, name='delete'),
    path('<int:offer_id>/toggle_active', views.toggle_active, name='toggle_active'),
    path('<int:offer_id>/delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('<int:offer_id>/update', views.update, name='update'),
    path('<int:offer_id>/edit', views.edit, name='edit'),
    path('ajax_toggle_favourite', views.ajax_toggle_favourite, name='ajax_toggle_favourite'),

    path("create_js/", views.create_js, name='create_js'),
]