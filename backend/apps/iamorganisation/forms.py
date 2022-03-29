from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation


from apps.accounts.models import User
from apps.iamorganisation.models import Organisation
from apps.accounts.forms import PhoneNumberField

class OrganisationFormO(ModelForm):
    phoneNumber = PhoneNumberField(label='',widget=forms.TextInput(attrs={'placeholder': _("Telefonnummer")}))
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
            "country",
            "organisationName",
            "contactPerson",
            "appearsInMap", # do we need this?
            "clubNumber",
            "streetNameAndNumber",           
        )

        labels = {
            "postalCode": '',
            "country": '',
            "organisationName": '',
            "contactPerson": '',
            "appearsInMap": '',
            "clubNumber": '',
            "streetNameAndNumber": '',            
        }
        
        widgets = {
            'postalCode': forms.TextInput(attrs={'placeholder': _("Postleitzahl")}),
            'country': forms.TextInput(attrs={'placeholder': _("Land")}),
            'organisationName': forms.TextInput(attrs={'placeholder': _("Offizieller Name Ihrer Organisation")}),
            'contactPerson': forms.TextInput(attrs={'placeholder': _("Name der Kontaktperson")}),
            'appearsInMap': forms.TextInput(attrs={'placeholder': _("Auf der Karte sichtbar und kontaktierbar für Helfende sein")}),
            'clubNumber': forms.TextInput(attrs={'placeholder': _("Vereinsnummer")}),
            'streetNameAndNumber': forms.TextInput(attrs={'placeholder': _("Straße und Hausnummer")}),
        }
        
    def __init__(self, *args, **kwargs):
        super(OrganisationFormO, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_survey"


        self.helper.layout = Layout(
            Row(Column("organisationName"), Column("contactPerson")),
            Row(Column("phoneNumber"), Column("email")),
            Row(Column("clubNumber"), Column("country")),
            Row(Column("postalCode"), Column("streetNameAndNumber")),
            Row(Column("password1"), Column("password2")),
            HTML(
                '<div class="registration_disclaimer">{}</div>'.format(
                    _(
                        'Hiermit bestätige ich die <a target="_blank" href="/dataprotection/">Datenschutzbedingungen</a>.'
                    )
                )
            ),
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


class OrganisationForm(OrganisationFormO):
    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.helper.add_input(
            Submit(
                "submit",
                "Jetzt registrieren",
                onclick="this.form.submit(); this.disabled=true; this.value='Sending…';",
            )
        )

class OrganisationFormExtra(OrganisationFormO):
    def __init__(self, *args, **kwargs):
        super(OrganisationFormExtra, self).__init__(*args, **kwargs)
        # !!! namen der knöpe dürfen nicht verändert werden, sonst geht code woanders kaputt
        self.helper.add_input(Submit("submit", _("Schicke Mails")))
        self.helper.add_input(Submit("submit", _("Schicke Mails + Erstelle Anzeige")))


class OrganisationFormEditProfile(OrganisationFormO):
    class Meta:
        model = Organisation
        exclude = [
            "uuid",
            "user",
            "approvalDate",
            "approvedBy",
        ]

        labels = {
            "postalCode": _("Postleitzahl"),
            "country": _("Land"),
            "generalInfo": _(
                "Text Ihrer Suchanzeige. Wird nur öffentlich gezeigt wenn Sie auf der Karte sichtbar sind und kontaktbierbar sein möchten. Hier können Sie genau beschreiben, für welche Rollen Sie Unterstützung brauchen, welche Qualifikationen dafür notwendig sind, und unter welchen Bedingungen (z.B. Bezahlung) gesucht wird."
            ),
            "organisationName": _("Offizieller Name Ihrer Institution"),
            "contactPerson": _("Name der Kontaktperson"),
            "appearsInMap": _("Auf der Karte sichtbar und kontaktierbar für Helfende sein"),
        }

    def __init__(self, *args, **kwargs):
        super(OrganisationFormEditProfile, self).__init__(*args, **kwargs)
        self.fields["generalInfo"].required = False
        # self.fields['appears_in_map'].required = False
        self.helper.add_input(
            Submit("submit", _("Daten aktualisieren"), css_class="btn blue text-white btn-md",)
        )
        self.helper.layout = Layout(
            Row(Column("organisationName"), Column("contactPerson")),  # Row(Column('appears_in_map')),
            Row(Column("phoneNumber")), # TODO phone number not showing yet ( -> is stored in user)
            Row(Column("postalCode"), Column("country")),
        )


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

class PostingForm(forms.ModelForm):
    class Meta:
        model = Organisation
        labels = {
            "appearsInMap": _("Anzeige soll angezeigt werden"),
            "generalInfo": _("Anzeigetext"),
        }
        fields = ["appearsInMap", "generalInfo"]

    def __init__(self, *args, **kwargs):
        super(PostingForm, self).__init__(*args, **kwargs)
        self.fields["generalInfo"].required = False
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            HTML(
                '<script type="text/javascript" src="{}"></script>'.format(
                    static("js/PostingForm.js")
                )
            ),
            "appearsInMap",
            "generalInfo",
        )
        self.helper.add_input(
            Submit("submit", _("Anzeige aktualisieren"), css_class="btn blue text-white btn-md",)
        )
