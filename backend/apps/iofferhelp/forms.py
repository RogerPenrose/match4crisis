from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit

from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.accounts.forms import CustomUserCreationForm, SpecialPreferencesForm
from apps.offers.models import GenericOffer
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
        user = super().save(commit)
        user.isHelper = True
        if(commit):
            user.save()
        helper = Helper.objects.create(user=user)
        # TODO add more fields as necessary
        if(commit):
            helper.save()
        return user, helper

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
            if abbr != "DO":
                svg =  open('static/img/icons/icon_'+abbr+'.svg', 'r').read()
                self.fields[abbr] = forms.BooleanField(required=False, label=str(svg)+str(offerType) ) # TODO change/remove the label

        self.helper.add_input(Submit("submit", _("Weiter")))


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
