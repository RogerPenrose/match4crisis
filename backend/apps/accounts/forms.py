from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils.text import capfirst
from django.utils.html import format_html

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit

from django_select2 import forms as s2forms

from match4crisis.constants.choices import GENDER_CHOICES

from .models import User

class PhoneNumberField(forms.CharField):
    """Custom form field for Phone numbers"""
    default_validators = [validators.RegexValidator(regex = r"^\+?1?\d{8,15}$", message=_("Bitte geben Sie eine gültige Telefonnummer ein."))]

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating both Refugees and Helpers (Organisations have a more complex form)"""
    acceptTerms = forms.BooleanField(required=True, label=_('Ich habe die <a target="_blank" href="/dataprotection/">Datenschutzerklärung</a> gelesen und bin damit einverstanden'))

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "gender",
        )
        labels={
            "first_name": "",
            "last_name": "",
            "email": "",
            "gender": "",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": _("Vorname(n)")}),
            "last_name": forms.TextInput(attrs={"placeholder": _("Nachname(n)")}),
            "email": forms.TextInput(attrs={"placeholder": _("E-Mail")}),
        }

        field_classes = {"email": forms.EmailField}

    field_order = ["first_name", "last_name", "email", "password1", "password2", "gender", "acceptTerms"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = False

        self.fields["gender"] = forms.ChoiceField(label = "", choices=(('', _('Geschlecht auswählen')),) + GENDER_CHOICES, help_text='<a href="" id="genderHintAnchor" data-toggle="modal" data-target="#genderHintModal"> %s </a>' % _("Warum wir nach deinem Geschlecht fragen"))

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

        for f in self.fields:
            self.fields[f].required = False

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
        "invalid_login": _("Falsche E-Mail-Adresse oder falsches Passwort. Bitte überprüfe deine Eingabe."),
        "inactive": _("Dieser Account wurde deaktiviert. Bitte melde dich beim Support wenn du denkst, dass dein Account zu unrecht deaktiviert wurde."),
        "email_not_confirmed" : format_html('{error_msg}: <a href="{href}">{link_content}</a>',
            error_msg = _("Bitte bestätige zunächst deine E-Mail-Adresse. Falls du keine Bestätigung-E-Mail erhalten hast, kannst du hier eine Neue anfordern"), 
            href = "/accounts/thanks", # reversing results in a circular import error even with reverse_lazy, as this dict is evaluated at startup -> reverse_lazy('thanks'),
            link_content = _("Neue Bestätigungs-E-Mail anfordern")
        ),
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
        Also disallows login by users who have not confirmed their email address.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """

        if not user.validatedEmail:
            raise ValidationError(
                self.error_messages["email_not_confirmed"],
                code="email_not_confirmed",
            )

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

def check_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(_("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits"))
    return value

def email_exists_or_already_validated(value):
    try:
        u = User.objects.get(email=value)
        if u.validatedEmail:
            raise ValidationError(_("Diese E-Mail-Adresse wurde bereits bestätigt."))
    except User.DoesNotExist:
        raise ValidationError(_("Es ist noch kein Nutzer mit diese E-Mail-Adresse registriert."))

class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label=_("Neue E-Mail-Adresse"), validators=[check_unique_email])

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-changeEmailForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "change_email"

        self.helper.add_input(Submit("submit", _("E-Mail-Adresse ändern")))

class ResendConfirmationEmailForm(forms.Form):
    email = forms.EmailField(label=_("E-Mail-Adresse"), validators=[email_exists_or_already_validated])

    def __init__(self, *args, **kwargs):
        super(ResendConfirmationEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-resendConfirmationEmailForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "resend_confirmation_email"

        self.helper.add_input(Submit("submit", _("Neue Bestätigungs-E-Mail anfordern")))