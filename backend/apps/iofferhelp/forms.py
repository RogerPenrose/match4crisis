from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django.conf import settings

from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.accounts.forms import CustomUserCreationForm, SpecialPreferencesForm
from apps.offers.models import *
from .models import Helper

class HelperCreationForm(CustomUserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super(HelperCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-helperCreationForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "signup_helper"

        self.fields['email'].required = True

        self.helper.add_input(Submit("submit", _("Registrieren")))


    def save(self, commit: bool = ...):
        user = super().save(False)
        user.isHelper = True
        # In Prod: user should be inactive (unable to log in) until email is confirmed
        # Bypass email confirmation in Dev (where settings.DEBUG is True)
        user.is_active = settings.DEBUG
        if(commit):
            user.save()
        helper = Helper.objects.create(user=user)
        # TODO add more fields as necessary
        if(commit):
            helper.save()
        return user, helper
class ChooseHelpForm(forms.Form):
    

    # We need to Define what the user offers via the selected subcategories. Hence we need to build this form by having 
    # One bool field per subcategory, with a class or something, associating this field with its parent category.
    tr_svg = open('static/img/icons/icon_TR.svg', 'r').read()
    bu_svg = open('static/img/icons/icon_BU.svg', 'r').read()
    we_svg = open('static/img/icons/icon_WE.svg', 'r').read()
    transportation_people = forms.BooleanField(required=False, label=str(tr_svg)+str(_("Personenfahrten")), widget=forms.CheckboxInput(attrs={"class": "subcategory transportation"}) )
    transportation_goods = forms.BooleanField(required=False, label=str(tr_svg)+str(_("Gütertransport")), widget=forms.CheckboxInput(attrs={"class": "subcategory transportation"}))
    buerocracy_translation = forms.BooleanField(required=False, label=str(bu_svg)+str(_("Übersetzungen")), widget=forms.CheckboxInput(attrs={"class": "subcategory buerocracy"}))
    buerocracy_companion = forms.BooleanField(required=False, label=str(bu_svg)+str(_("Begleitung bei Amtsgängen")), widget=forms.CheckboxInput(attrs={"class": "subcategory buerocracy"}))
    buerocracy_legal = forms.BooleanField(required=False, label=str(bu_svg)+str(_("Juristische Hilfe")), widget=forms.CheckboxInput(attrs={"class": "subcategory buerocracy"}))
    buerocracy_other = forms.BooleanField(required=False, label=str(bu_svg)+str(_("Anderes")), widget=forms.CheckboxInput(attrs={"class": "subcategory buerocracy"}))
    welfare_elderly = forms.BooleanField(required=False, label=str(we_svg)+str(_("Altenpflege")), widget=forms.CheckboxInput(attrs={"class": "subcategory welfare"}))
    welfare_psych = forms.BooleanField(required=False, label=str(we_svg)+str(_("Psychologische Hilfe")), widget=forms.CheckboxInput(attrs={"class": "subcategory welfare"}))
    welfare_disabled = forms.BooleanField(required=False, label=str(we_svg)+str(_("Behindertenpflege")), widget=forms.CheckboxInput(attrs={"class": "subcategory welfare"}))
    def __init__(self, *args, **kwargs):
        super(ChooseHelpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-chooseHelpForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "choose_help"
        for abbr, offerType in GenericOffer.OFFER_CHOICES:
            if abbr != "DO" and abbr !="TL" and abbr !="BU" and abbr !="WE" and abbr!="TR":
                svg =  open('static/img/icons/icon_'+abbr+'.svg', 'r').read()
                self.fields[abbr] = forms.BooleanField(required=False, label=str(svg)+str(offerType)) # TODO change/remove the label
          
        self.fields["NA"] = forms.BooleanField(required=False, label=_("Unklar"))
        self.helper.add_input(Submit("submit", _("Weiter")))

'''   
class ChooseHelpForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChooseHelpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-chooseHelpForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "choose_help"

        # Create a boolean field for every offer type
        for abbr, offerType in GenericOffer.OFFER_CHOICES:
            if abbr != "DO" :
                svg =  open('static/img/icons/icon_'+abbr+'.svg', 'r').read()
                self.fields[abbr] = forms.BooleanField(required=False, label=str(svg)+str(offerType) ) # TODO change/remove the label
        self.fields["NA"] = forms.BooleanField(required=False, label=_("Unklar"))
        self.helper.add_input(Submit("submit", _("Weiter")))
'''

class HelperPreferencesForm(SpecialPreferencesForm):
    class Meta:
        model = Helper
        fields=(   
        )

        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(HelperPreferencesForm, self).__init__(*args, **kwargs)
        self.helper.form_id = "id-helperPreferencesForm"
