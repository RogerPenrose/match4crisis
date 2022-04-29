from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation


from apps.accounts.models import User
from apps.accounts.forms import PhoneNumberField, SpecialPreferencesForm
from .models import DonationRequest, HelpRequest, MaterialDonationRequest, Organisation


class OrganisationFormO(ModelForm):
    phoneNumber = PhoneNumberField(label='',widget=forms.TextInput(attrs={'placeholder': _("Telefonnummer")}))
    acceptTerms = forms.BooleanField(required=True, label=_('Ich habe die <a target="_blank" href="/dataprotection/">Datenschutzerklärung</a> gelesen und bin damit einverstanden'))
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": _("Passwort")}),
        strip=False,
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": _("Passwort bestätigen")}),
        strip=False,
    )

    class Meta:
        model = Organisation

        fields=(
            "postalCode",
            "city",
            "country",
            "organisationName",
            "contactPerson",
            "streetNameAndNumber",           
        )

        labels = {
            "postalCode": '',
            "country": '',
            "city": '',
            "organisationName": '',
            "contactPerson": '',
            "streetNameAndNumber": '',            
        }
        
        widgets = {
            'postalCode': forms.TextInput(attrs={'placeholder': _("Postleitzahl")}),
            'city': forms.TextInput(attrs={'placeholder': _("Stadt")}),
            #'country': forms.ChoiceWidget(attrs={'placeholder': _("Land")}),
            'organisationName': forms.TextInput(attrs={'placeholder': _("Offizieller Name Ihrer Organisation")}),
            'contactPerson': forms.TextInput(attrs={'placeholder': _("Name der Kontaktperson")}),
            'streetNameAndNumber': forms.TextInput(attrs={'placeholder': _("Straße und Hausnummer")}),
        }
        
    def __init__(self, *args, **kwargs):
        super(OrganisationFormO, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_survey"

        self.fields['country'].empty_label = _("Land")
        self.fields['country'].widget.attrs['class'] = 'main'


        self.helper.layout = Layout(
            Row(Column("organisationName"), Column("contactPerson")),
            Row(Column("phoneNumber"), Column("email")),
            Row(Column("country"), Column("postalCode")),
            Row(Column("city"), Column("streetNameAndNumber")),
            Row(Column("password1"), Column("password2")),
            Row("acceptTerms"),
        )
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

class OrganisationPreferencesForm(SpecialPreferencesForm):
    class Meta:
        model = Organisation
        fields=(
            "organisationName",
            "contactPerson",
            "logo",
            "country",
            "postalCode",
            "city",
            "streetNameAndNumber",  
            "about",   
        )

        labels = {
            "streetNameAndNumber": _("Straße und Hausnummer"),
            "postalCode": _("Postleitzahl"),
            "city": _("Stadt"),
            "country": _("Land"),
            "organisationName": _("Offizieller Name Ihrer Institution"),
            "contactPerson": _("Name der Kontaktperson"),
            "logo": _("Logo Ihrer Organisation"),
            "about": _("Über Ihre Institution")
        }

    def __init__(self, *args, **kwargs):
        super(OrganisationPreferencesForm, self).__init__(*args, **kwargs)
        self.helper.form_id = "id-organisationPreferencesForm"


def check_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(_("Diese Email ist bereits vergeben"))
    return value

class OrganisationFormInfoSignUp(OrganisationFormO):
    email = forms.EmailField(
        validators=[check_unique_email], label='', widget=forms.EmailInput(attrs={'placeholder':_("Offizielle E-Mail-Adresse der Kontaktperson")}) 
    )
   
class OrganisationFormInfoCreate(OrganisationFormO):
    # Used internally to bypass duplicate email validation
    email = forms.EmailField()

class HelpRequestForm(forms.ModelForm):
    # TODO also allow digital offers?
    RADIUS_CHOICES = [
        ('', _('Radius')),
        (5, "<5km"),
        (10, "<10km"),
        (20, "<20km"),
        (50, "<50km"),
    ]

    images = forms.ImageField(label=_('Laden Sie hier optional Bilder hoch.'), widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}), required=False)

    class Meta:
        model = HelpRequest
        fields = (
            'title',
            'description',
            'location',
            'lat',
            'lng',
            'bb',
            'radius',
        )
        labels = {
            'title' : _('Titel'),
            'description' : _('Beschreibung'),
            'location' : _('Ort')
        }
        widgets = {
            'lat' : forms.HiddenInput(),
            'lng' : forms.HiddenInput(),
            'bb' : forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(HelpRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-helpRequestForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "request_help"

        self.fields['radius'] = forms.TypedChoiceField(choices=self.RADIUS_CHOICES, coerce=int, label='', help_text=_("Es werden E-Mails an Helfer ausgesendet, die in diesem Radius ihre Hilfe anbieten."))

        self.helper.add_input(Submit("submit", _("Speichern")))

class DonationRequestForm(forms.ModelForm):

    images = forms.ImageField(label=_('Laden Sie hier optional Bilder hoch.'), widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}), required=False)

    class Meta:
        model = DonationRequest
        fields = (
            'title',
            'description',
            'beneficiary',
            'iban',
            'reason',
        )
        labels = {
            'title' : _("Titel"),
            'description' : _("Beschreibung"),
        }

    def __init__(self, *args, **kwargs):
        super(DonationRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-donationRequestForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "request_donations"

        self.helper.add_input(Submit("submit", _("Speichern")))

class MaterialDonationRequestForm(forms.ModelForm):

    images = forms.ImageField(label=_('Laden Sie hier optional Bilder hoch.'), widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}), required=False)

    class Meta:
        model = MaterialDonationRequest
        fields = (
            'title',
            'donationType',
            'description',
            'location',
            'lat',
            'lng',
            'bb',
        )
        labels = {
            'title' : _('Titel'),
            'donationType' : _('Art der Sachspende'),
            'description' : _('Beschreibung'),
            'location' : _('Ort')
        }
        widgets = {
            'lat' : forms.HiddenInput(),
            'lng' : forms.HiddenInput(),
            'bb' : forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(MaterialDonationRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-materialDonationRequestForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "create_material_donation_request"

        self.helper.add_input(Submit("submit", _("Speichern")))