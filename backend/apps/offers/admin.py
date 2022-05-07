from django.contrib import admin

from .models import BuerocraticOffer, ChildcareOffer, WelfareOffer, ManpowerOffer, JobOffer,GenericOffer,AccommodationOffer,TransportationOffer, TranslationOffer

admin.site.register(GenericOffer)
admin.site.register(AccommodationOffer)
admin.site.register(TransportationOffer)
admin.site.register(TranslationOffer)
admin.site.register(BuerocraticOffer)
admin.site.register(ChildcareOffer)
admin.site.register(WelfareOffer)
admin.site.register(ManpowerOffer)
admin.site.register(JobOffer)
