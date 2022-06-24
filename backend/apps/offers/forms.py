from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
from crispy_forms.helper import FormHelper
import logging
from .models import *

# Labels for the input fields. If there need to be different labels depending on if the offer is a request for help,
# the entry should be a tuple where the first value is used if it isn't a request for help and the second if it is.
LABELS = {
    GenericOffer : {
        'offerTitle' : _("Titel"),
        'offerDescription' : _("Beschreibung"),
        'location' : _("Ort"),
        'toggleCost' : (_("Ich wünsche eine Bezahlung"), _("Ich wäre bereit, für die Hilfe zu bezahlen")),
        'cost' : (_("Gewünschte Bezahlung"), _("Wie viel wärst du bereit zu zahlen?"))
    },
    AccommodationOffer : {
        "startDateAccommodation" : (_("Ab wann kannst du die Unterkunft anbieten?"), _("Ab wann benötigst du eine Unterkunft?")),
        "numberOfPeople" : (_("Maximale Anzahl der Bewohner"), _("Gewünschte Anzahl der Bewohner") ),
        "petsAllowed": (_("Haustiere sind gestattet"), _("Ich habe Haustiere dabei")),
        "typeOfResidence" : (_("Art der Unterbringung"), _("Gewünschte Art der Unterbringung")),
    },
    TranslationOffer : {
        "languages" : (_("Zwischen welchen Sprachen kannst du übersetzen?"), _("Zwischen welchen Sprachen suchst du Übersetzungen?"))
    },
    TransportationOffer : {
        "numberOfPassengers" : (_("Wie viele Passagiere könnten mitfahren?"), _("Wie viele Passagiere werden erwartet?")),
        "distance" : (_("Wie weit bist du bereit zu fahren?"), _("Wie weit muss gefahren werden?")),
        "typeOfCar": _("Fahrzeugtyp")
    },
    BuerocraticOffer : {
    },
    ManpowerOffer : {
        "distanceChoices" : _("Wie weit sollte der Einsatzort maximal entfernt sein?"),
        "canGoforeign": (_("Ich bin bereit für einen Auslandseinsatz"), _("Helfer*in sollte bereit für einen Auslandseinsatz sein")),
        "hasExperience_crisis": (_("Ich habe Erfahrung mit Krisenmanagement"), _("Helfer*in sollte Erfahrung mit Krisenmanagement haben")),
        "hasMedicalExperience": (_("Ich habe eine medizinische Ausbildung"), _("Helfer*in sollte medizinische Ausbildung haben")),
        "hasDriverslicense": (_("Ich habe einen Führerschein"), _("Helfer*in sollte einen Führerschein haben")),
        "describeMedicalExperience": _("Beschreibe den Umfang deiner medizinischen Erfahrung"),
    },
    ChildcareOffer : {
        "helpType_childcare" : (_("Welche Art von Betreuung kannst du bieten?"), _("Welche Art von Betreuung suchst du?")),
        "timeOfDay": _("Zeitraum der Betreuung"),
        "distance": (_("In welchem Umkreis bist du bereit zu helfen?"), _("In welchem Umkreis sollte der/die Helfer*in wohnen?")),
        "numberOfChildren": (_("Wie viele Kinder könntest du maximal betreuen?"), _("Anzahl der Kinder")),
        "hasSpace": _("Ich habe Räumlichkeiten bei mir"),
        "hasEducation": (_("Ich habe eine spezielle Ausbildung"), _("Helfer*in sollte eine spezielle Ausbildung haben")) ,
        "hasExperience": (_("Ich habe Betreuungserfahrung"), _("Helfer*in sollte Betreuungserfahrung haben")),
        "isRegular": (_("Ich kann regelmäßig betreuen"), _("Regelmäßige Betreuung erwünscht"))
    },
    WelfareOffer : {
        "hasEducation_welfare":  (_("Ich habe medizinische Erfahrung"), _("Helfer*in sollte medizinische Erfahrung haben")),
        "typeOfEducation": _("Beschreibe den Umfang deiner medizinischen Erfahrung")
    },
    JobOffer : {
        "jobType" : _("Arbeitsfeld"),
        "jobTitle" : _("Jobtitel"),
        "requirements" : _("Anforderungen"),
    }
}

logger = logging.getLogger("django")


class OfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rfh = self.instance.requestForHelp if hasattr(self.instance, 'requestForHelp') else self.instance.genericOffer.requestForHelp
        for fieldName, field in self.fields.items():
            logger.info(fieldName)
            field.widget.attrs.update({'class': 'form-control'})
            try:
                labelEntry = LABELS[self.Meta.model][fieldName]
                field.label = labelEntry[rfh] if type(labelEntry) is tuple else labelEntry
            except KeyError:
                pass

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

class GenericForm(OfferForm):
    toggleCost = forms.BooleanField(required=False)

    class Meta:
        attrs = { "class": "form-control"}
        model = GenericOffer

        fields = ["offerType", "offerTitle", "offerDescription","location", "lat","lng", "bb", "cost"]

        widgets = {
            'location': forms.TextInput(attrs={ 'class': 'form-control'}),
            'offerType' : forms.HiddenInput(),
            'lat' : forms.HiddenInput(),
            'lng' : forms.HiddenInput(),
            'bb' : forms.HiddenInput()
        }

    field_order = ["offerTitle", "offerDescription", "location", "toggleCost", "cost"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.offerType == 'TR':
            self.fields['location'].label = _("Startpunkt")
        elif self.instance.offerType == 'JO':
            self.fields['toggleCost'].widget = forms.HiddenInput(attrs={'checked' : True})
            self.fields['cost'].label = _("Welchen Stundenlohn würdest du dir wünschen?") if self.instance.requestForHelp else _("Stundenlohn")
        elif self.instance.offerType == 'AC':
            self.fields['toggleCost'].label = _("Ich wäre bereit, Miete zu zahlen") if self.instance.requestForHelp else _("Ich würde mir etwas Miete wünschen")
            self.fields['cost'].label = _("Wie viel wärst du bereit täglich zu bezahlen?") if self.instance.requestForHelp else _("Welche Tagesmiete würdest dir wünschen?")
        elif self.instance.offerType == 'CL' or self.instance.offerType == 'WE' or self.instance.offerType == 'MP':
            self.fields['cost'].label = _("Welchen Stundenlohn wärst du bereit zu bezahlen?") if self.instance.requestForHelp else _("Welchen Stundenlohn würdest dir wünschen?")
 
class JobForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = JobOffer
        exclude = ("genericOffer",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.genericOffer.requestForHelp:
            del self.fields['requirements']

class ChildcareForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ChildcareOffer
        exclude = ("genericOffer",)

        widgets = {
            'numberOfChildren' : forms.NumberInput(attrs={'min' : '1'})
        }

    
    field_order = ["helpType_childcare", "timeOfDay", "numberOfChildren", "isRegular", "hasExperience", "hasEducation", "hasSpace", "distance"]

class ManpowerForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = ManpowerOffer
        exclude = ("genericOffer",)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.genericOffer.requestForHelp:
            del self.fields['distanceChoices']
            del self.fields['describeMedicalExperience']

class WelfareForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = WelfareOffer
        exclude = ("genericOffer",)

        widgets = {
            'helpType' : forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.genericOffer.requestForHelp:
            del self.fields['typeOfEducation']
      
class BuerocraticForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = BuerocraticOffer
        exclude = ("genericOffer",)

        widgets = {
            'helpType' : forms.HiddenInput()
        }

class TransportationForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TransportationOffer
        exclude = ("genericOffer",)

        widgets = {
            'numberOfPassengers' : forms.NumberInput(attrs={'min' : '1'}),
            'helpType' : forms.HiddenInput()
        }
    
    field_order = ["numberOfPassengers", "typeOfCar", "distance"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.genericOffer.requestForHelp or self.instance.helpType == 'PT':
            self.fields['typeOfCar'].widget = forms.HiddenInput()
        if self.instance.helpType == 'GT':
            self.fields['numberOfPassengers'].widget = forms.HiddenInput()

class TranslationForm(OfferForm):
    class Meta:
        attrs = { "class": "form-control"}
        model = TranslationOffer
        exclude = ("genericOffer",)

        widgets = {
            "languages" : s2forms.Select2MultipleWidget()
        }

      
class AccommodationForm(OfferForm):

    class Meta:
        attrs = { "class": "form-control"}
        model = AccommodationOffer
        exclude = ("genericOffer",)

        widgets = {
            "startDateAccommodation" : forms.DateInput(format="%Y-%m-%d",attrs={'class':'form-control', 'type': 'date'}),
            "numberOfPeople" : forms.NumberInput(attrs={'min' : '1'})
        }

        help_texts = {
            "petsAllowed" : _("Bitte weise in der Beschreibung auf Genaueres hin.")
        }

    field_order = ["typeOfResidence", "numberOfPeople", "petsAllowed", "startDateAccommodation"]

class ImageForm(forms.Form):
    
    image = forms.ImageField(label=_("Hier kannst du optional Bilder hochladen"), widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': 'on'}), required=False)
    image.url = forms.CharField(required=False)
    image_id = forms.IntegerField(widget = forms.HiddenInput(),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
      
# TODO when adding new offer types this needs to be updated
OFFER_FORMS = {
    'AC' : AccommodationForm,
    'TL' : TranslationForm,
    'TR' : TransportationForm,
    'BU' : BuerocraticForm,
    'CL' : ChildcareForm,
    'WE' : WelfareForm,
    'MP' : ManpowerForm,
    'JO' : JobForm,
}

RADIUS_CHOICES = (
    ('', _("Umkreis wählen")),
    (0, "0km"),
    (1, "1km"),
    (2, "2km"),
    (5, "5km"),
    (10, "10km"),
    (20, "20km"),
    (50, "50km"),
)

OFFER_DESCRIPTIONS = {
    'AC' : _('Vorübergehender oder längerfristiger Wohnraum'),
    'TL' : _('z.B. für offizielle Dokumente'),
    'TR' : _('Transport von Personen oder Hilfsgütern'),
    'BU' : _('z.B. Unterstützung bei Behördengängen'),
    'CL' : _('Babysitting oder einfach nur Zeit verbringen'),
    'WE' : _('z.B. für ältere Personen oder Personen mit Behinderungen'),
    'MP' : _('Anpacken dort wo Hilfe gebraucht wird'),
    'JO' : _('Jobangebote speziell für Hilfesuchende'),
}


class LocationSearchForm(forms.Form):
    location = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'placeholder' : _('Gib hier einen Standort ein...'), 'class' : 'form-control'}))
    lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    bb = forms.CharField(required=False, widget=forms.HiddenInput())
    radius = forms.ChoiceField(required=False, label='', choices=RADIUS_CHOICES, widget=forms.Select(attrs={'class' : 'form-control'}))

    def __init__(self, *args, emptyChoice=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not emptyChoice:
            self.fields["radius"].choices = RADIUS_CHOICES[1:]


class OfferTypeSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for abbr, label in GenericOffer.OFFER_CHOICES:
            self.fields[abbr] = forms.BooleanField(required=False, label=label, help_text=OFFER_DESCRIPTIONS[abbr])
