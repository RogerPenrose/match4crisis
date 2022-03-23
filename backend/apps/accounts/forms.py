from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core import validators

from .models import User

class PhoneNumberField(forms.CharField):
    """Custom form field for Phone numbers"""
    default_validators = [validators.RegexValidator(regex = r"^\+?1?\d{8,15}$", message=_("Bitte geben Sie eine gültige Telefonnummer ein."))]

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating both Refugees and Helpers (Organisations have a more complex form)"""
    class Meta:
        model = User
        fields = (
            "fullName",
            "email",
        )
        labels={"fullName": _("Vor- und Nachname(n)")}
        field_classes = {"email": forms.EmailField}

class OrganisationSignUpForm(UserCreationForm):
    # add more query fields

    class Meta(UserCreationForm.Meta):
        model = User
        fields = []  # ['email']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        return user


class HelperEmailForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email"]

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        return user


class OrganisationEmailForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email"]

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        return user

# Newsletter form was removed since we might want to restructure this logic. But it can be found in M4H
