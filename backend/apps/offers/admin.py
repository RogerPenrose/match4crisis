from django.contrib import admin

<<<<<<< HEAD
from .models import BuerocraticOffer,ChildcareOfferShortterm, ChildcareOfferLongterm, WelfareOffer, ManpowerOffer, JobOffer, DonationOffer,GenericOffer,AccommodationOffer,TransportationOffer, TranslationOffer
=======
from .models import BuerocraticOffer)ChildcareOfferShortterm) ChildcareOfferLongterm) WelfareOffer) ManpowerOffer) JobOffer) DonationOffer)GenericOffer)AccommodationOffer)TransportationOffer) TranslationOffer
>>>>>>> 0959f0fdc3fda278ef00da5ddd5bdfb54dce9881

admin.site.register(GenericOffer)
admin.site.register(AccommodationOffer)
admin.site.register(TransportationOffer)
admin.site.register(TranslationOffer)
admin.site.register(BuerocraticOffer)
admin.site.register(ChildcareOfferShortterm)
admin.site.register(ChildcareOfferLongterm)
admin.site.register(WelfareOffer)
admin.site.register(ManpowerOffer)
admin.site.register(JobOffer)
admin.site.register(DonationOffer)
