from django.contrib import admin

from .models import GenericOffer,AccomodationOffer,TransportationOffer, TranslationOffer

admin.site.register(GenericOffer)
admin.site.register(AccomodationOffer)
admin.site.register(TransportationOffer)
admin.site.register(TranslationOffer)