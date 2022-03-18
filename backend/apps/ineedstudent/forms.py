from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.iamstudent.models import EmailToHospital
from apps.ineedstudent.models import Hospital

#Auf neuen Usecase anpassen

class HospitalFormO(ModelForm):
    class Meta:
        model = Hospital
        exclude = [
            "uuid",
            "registration_date",
            "user",
            "sonstige_infos",
            "max_mails_per_day",
            "appears_in_map",
            "approval_date",
            "approved_by",
        ]

        labels = {
            "plz": _("Postleitzahl"),
            "countrycode": _("Land"),
            "firmenname": _("Offizieller Name Ihrer Institution"),
            "ansprechpartner": _("Name der Kontaktperson"),
            "appears_in_map": _("Auf der Karte sichtbar und kontaktierbar für Helfende sein"),
        }

    def __init__(self, *args, **kwargs):
        super(HospitalFormO, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_survey"

        self.helper.layout = Layout(
            Row(Column("firmenname"), Column("ansprechpartner")),
            Row(Column("telefon"), Column("email")),
            Row(Column("plz"), Column("countrycode")),
            HTML('<hr style="margin-top: 20px; margin-bottom:30px;">'),
            HTML(
                '<div class="registration_disclaimer">{}</div>'.format(
                    _(
                        'Wir benötigen die Information, die Sie uns zur Verfügung stellen, um Helfende und Hilfesuchende miteinander zu vernetzen. Informationen dazu, welche personenbezogenen Daten bei dem Besuch und der Nutzung der Angebote auf unserer Seite erhoben und verarbeitet werden finden Sie in unseren Datenschutzbestimmungen (Link: <a target="_blank" href="/dataprotection/">https://match4crisis.de/dataprotection/</a>).'
                    )
                )
            ),
        )


class HospitalForm(HospitalFormO):
    def __init__(self, *args, **kwargs):
        super(HospitalForm, self).__init__(*args, **kwargs)
        self.helper.add_input(
            Submit(
                "submit",
                "Jetzt registrieren",
                onclick="this.form.submit(); this.disabled=true; this.value='Sending…';",
            )
        )

#kann weg?
class HospitalFormExtra(HospitalFormO):
    def __init__(self, *args, **kwargs):
        super(HospitalFormExtra, self).__init__(*args, **kwargs)
        # !!! namen der knöpe dürfen nicht verändert werden, sonst geht code woanders kaputt
        self.helper.add_input(Submit("submit", _("Schicke Mails")))
        self.helper.add_input(Submit("submit", _("Schicke Mails + Erstelle Anzeige")))


class HospitalFormEditProfile(HospitalFormO):
    class Meta:
        model = Hospital
        exclude = [
            "uuid",
            "registration_date",
            "user",
            "max_mails_per_day",
            "approval_date",
            "approved_by",
        ]

        labels = {
            "plz": _("Postleitzahl"),
            "countrycode": _("Land"),
            "sonstige_infos": _(
                "Text Ihrer Suchanzeige. Wird nur öffentlich gezeigt wenn Sie auf der Karte sichtbar sind und kontaktbierbar sein möchten. Hier können Sie genau beschreiben, für welche Rollen Sie Unterstützung brauchen, welche Qualifikationen dafür notwendig sind, und unter welchen Bedingungen (z.B. Bezahlung) gesucht wird."
            ),
            "firmenname": _("Offizieller Name Ihrer Institution"),
            "ansprechpartner": _("Name der Kontaktperson"),
            "appears_in_map": _("Auf der Karte sichtbar und kontaktierbar für Helfende sein"),
        }

    def __init__(self, *args, **kwargs):
        super(HospitalFormEditProfile, self).__init__(*args, **kwargs)
        self.fields["sonstige_infos"].required = False
        # self.fields['appears_in_map'].required = False
        self.helper.add_input(
            Submit("submit", _("Daten aktualisieren"), css_class="btn blue text-white btn-md",)
        )
        self.helper.layout = Layout(
            Row(Column("firmenname"), Column("ansprechpartner")),  # Row(Column('appears_in_map')),
            Row(Column("telefon")),
            Row(Column("plz"), Column("countrycode")),
        )


def check_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(_("Diese Email ist bereits vergeben"))
    return value


class HospitalFormInfoSignUp(HospitalFormO):
    email = forms.EmailField(
        validators=[check_unique_email], label=_("Offizielle E-Mail-Adresse der Kontaktperson"),
    )


class HospitalFormInfoCreate(HospitalFormO):
    # Used internally to bypass duplicate email validation
    email = forms.EmailField()


#Kann weg?
class EmailToHospitalForm(forms.ModelForm):
    class Meta:
        model = EmailToHospital
        fields = ["subject", "message"]
        labels = {"subject": _("Betreff"), "message": _("Nachrichtentext")}

        help_texts = {
            "message": _(
                "Gib hier deine Antwort auf das Angebot ein. Wer bist du? Welche Fähigkeiten bringst du für diese Stelle mit?"
            )
        }

    def __init__(self, *args, **kwargs):
        super(EmailToHospitalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", _("Hilfsangebot abschicken"), css_class="btn blue text-white btn-md",)
        )

    def clean_message(self):
        message = self.cleaned_data["message"]
        initial_message = self.initial["message"]
        if "".join(str(message).split()) == "".join(str(initial_message).split()):
            raise ValidationError(_("Bitte personalisiere diesen Text"), code="invalid")
        return message


class PostingForm(forms.ModelForm):
    class Meta:
        model = Hospital
        labels = {
            "appears_in_map": _("Anzeige soll angezeigt werden"),
            "sonstige_infos": _("Anzeigetext"),
        }
        fields = ["appears_in_map", "sonstige_infos"]

    def __init__(self, *args, **kwargs):
        super(PostingForm, self).__init__(*args, **kwargs)
        self.fields["sonstige_infos"].required = False
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            HTML(
                '<script type="text/javascript" src="{}"></script>'.format(
                    static("js/PostingForm.js")
                )
            ),
            "appears_in_map",
            "sonstige_infos",
        )
        self.helper.add_input(
            Submit("submit", _("Anzeige aktualisieren"), css_class="btn blue text-white btn-md",)
        )
