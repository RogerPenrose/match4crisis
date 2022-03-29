from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit

from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import CustomUserCreationForm
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
        user = super().save(commit)
        user.isRefugee = True
        if(commit):
            user.save()
        refugee = Refugee.objects.create(user=user)
        # TODO add more fields as necessary
        if(commit):
            refugee.save()
        return refugee
