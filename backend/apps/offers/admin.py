from django.contrib import admin

from .models import GenericOffer,AccommodationOffer,TransportationOffer, TranslationOffer

admin.site.register(GenericOffer)
admin.site.register(AccommodationOffer)
admin.site.register(TransportationOffer)
admin.site.register(TranslationOffer)