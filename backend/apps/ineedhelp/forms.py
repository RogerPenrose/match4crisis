from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django.conf import settings

from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import CustomUserCreationForm, SpecialPreferencesForm
from .models import Refugee

class RefugeeCreationForm(CustomUserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super(RefugeeCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-refugeeCreationForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "signup_refugee"

        self.fields['email'].required = True

        self.helper.add_input(Submit("submit", _("Registrieren")))


    def save(self, commit: bool = ...):
        user = super().save(False)
        user.isRefugee = True
        # In Prod: user should be unable to log in until email is confirmed
        # Bypass email confirmation in Dev (where settings.DEBUG is True)
        user.validatedEmail = settings.DEBUG
        if(commit):
            user.save()
        refugee = Refugee.objects.create(user=user)
        # TODO add more fields as necessary
        if(commit):
            refugee.save()
        return user, refugee

class RefugeePreferencesForm(SpecialPreferencesForm):
    class Meta:
        model = Refugee
        fields=(   
        )

        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(RefugeePreferencesForm, self).__init__(*args, **kwargs)
        self.helper.form_id = "id-refugeePreferencesForm"
