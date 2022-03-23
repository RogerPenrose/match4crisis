from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import User


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
        user.username = user.email
        user.save()
        return user


class OrganisationEmailForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email"]

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.username = user.email
        user.save()
        return user


class HelperSignUpForm(UserCreationForm):
    # add more query fields

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_helper = True
        user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(label=_("E-Mail"), widget=forms.TextInput(attrs={"autofocus": True}))


# Newsletter form was removed since we might want to restructure this logic. But it can be found in M4H
