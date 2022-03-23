from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.iamorganisation.models import Organisation

# TODO Auf neuen Usecase anpassen

class OrganisationFormO(ModelForm):
    class Meta:
        model = Organisation
        exclude = [
            "uuid",
            "user",
            "generalInfo",
            "appearsInMap",
            "approvalDate",
            "approvedBy",
        ]

        labels = {
            "postalCode": _("Postleitzahl"),
            "country": _("Land"),
            "organisationName": _("Offizieller Name Ihrer Organisation"),
            "contactPerson": _("Name der Kontaktperson"),
            "appearsInMap": _("Auf der Karte sichtbar und kontaktierbar für Helfende sein"),
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
            Row(Column("user.phoneNumber"), Column("email")), #TODO Phone number not showing yet
            Row(Column("postalCode"), Column("country")),
            HTML('<hr style="margin-top: 20px; margin-bottom:30px;">'),
            HTML(
                '<div class="registration_disclaimer">{}</div>'.format(
                    _(
                        'Wir benötigen die Information, die Sie uns zur Verfügung stellen, um Helfende und Hilfesuchende miteinander zu vernetzen. Informationen dazu, welche personenbezogenen Daten bei dem Besuch und der Nutzung der Angebote auf unserer Seite erhoben und verarbeitet werden finden Sie in unseren Datenschutzbestimmungen (Link: <a target="_blank" href="/dataprotection/">https://match4crisis.de/dataprotection/</a>).'
                    )
                )
            ),
        )


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
        validators=[check_unique_email], label=_("Offizielle E-Mail-Adresse der Kontaktperson"),
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
