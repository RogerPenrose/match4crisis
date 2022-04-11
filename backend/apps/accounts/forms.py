from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils.text import capfirst

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit

from django_select2 import forms as s2forms

from .models import User

class PhoneNumberField(forms.CharField):
    """Custom form field for Phone numbers"""
    default_validators = [validators.RegexValidator(regex = r"^\+?1?\d{8,15}$", message=_("Bitte geben Sie eine gültige Telefonnummer ein."))]

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating both Refugees and Helpers (Organisations have a more complex form)"""
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )
        labels={
            "first_name": "",
            "last_name": "",
            "email": "",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": _("Vorname(n)")}),
            "last_name": forms.TextInput(attrs={"placeholder": _("Nachname(n)")}),
            "email": forms.TextInput(attrs={"placeholder": _("E-Mail")}),
        }

        field_classes = {"email": forms.EmailField}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = False

        self.fields["password1"].label = ""
        self.fields["password2"].label = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["password1"].widget.attrs["placeholder"] = _("Passwort")
        self.fields["password2"].widget.attrs["placeholder"] = _("Passwort bestätigen")

        



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


class CommonPreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "spokenLanguages", # TODO By default a manytomany model field will be displayed as a MultipleChoiceField. Instead one should be able to search&add langs
            "phoneNumber",
            "sharePhoneNumber",
        )

        widgets = {
            "spokenLanguages" : s2forms.Select2MultipleWidget()
        }

    def __init__(self, *args, **kwargs):
        super(CommonPreferencesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-commonPreferencesForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "preferences"
        self.helper.form_tag = False

        if 'instance' in kwargs:
            if kwargs['instance'].isOrganisation:
                del self.fields["first_name"]
                del self.fields["last_name"]
                
class SpecialPreferencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SpecialPreferencesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-specialPreferencesForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "preferences"
        self.helper.form_tag = False

        self.helper.add_input(Submit("submit", _("Speichern")))
    

UserModel = get_user_model()


class CustomAuthenticationForm(forms.Form):

    """
    Custom class for authenticating users.
    Used instead of django.contrib.auth.AuthenticationForm in order to allow email/password login rather than username/password.
    """

    email = forms.EmailField(
    label=_("E-Mail"),
    widget=forms.TextInput(attrs={"autofocus": True, "placeholder": _("E-Mail*")}),
    )

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": _("Password*")}),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "email" field.
        self.email_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        email_max_length = self.email_field.max_length or 254
        self.fields["email"].max_length = email_max_length
        self.fields["email"].widget.attrs["maxlength"] = email_max_length
        if self.fields["email"].label is None:
            self.fields["email"].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"email": self.email_field.verbose_name},
        )

# Newsletter form was removed since we might want to restructure this logic. But it can be found in M4H
