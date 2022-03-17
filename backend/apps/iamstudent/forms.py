# from django.forms import *
import logging

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Field, HTML, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.iamstudent.custom_crispy import RadioButtons
from apps.iamstudent.models import AUSBILDUNGS_IDS, AUSBILDUNGS_TYPEN, EmailToSend, Student

form_labels = {
    "uuid": _("Writerekp"),
    "registration_date": _("Writer"),
    "name_first": _("Vorname"),
    "name_last": _("Nachname"),
    "phone_number": _("Telefonnummer"),
    "plz": _("Postleitzahl"),
    "countrycode": _("Land"),
    "email": _("Email"),
    "availability_start": _("Ich bin verfügbar ab"),
    "braucht_bezahlung": _("Ich benötige eine Vergütung"),
    # Form Labels for qualifications
    "ausbildung_typ_pflege": _(
        'Pflege <em>(melde Dich auch bei <a href="https://pflegereserve.de/#/login" target="_blank">Pflegereserve</a>)</em>'
    ),
    "ausbildung_typ_pflege_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_physio": _("Physiotherapeut*in"),
    "ausbildung_typ_physio_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_hebamme": _("Entbindungshelfer*in"),
    "ausbildung_typ_fsj": _("FSJ im Gesundheitswesen"),
    "ausbildung_typ_arzt_sonstige": _("Sonstige:"),
    "ausbildung_typ_medstud": _("Medizinstudent*in / Arzt / Ärztin"),
    "ausbildung_typ_medstud_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_medstud_famulaturen_anaesthesie": _("Anästhesie"),
    "ausbildung_typ_medstud_famulaturen_allgemeinmedizin": _("Allgemeinmedizin"),
    "ausbildung_typ_medstud_famulaturen_chirurgie": _("Chirurgie"),
    "ausbildung_typ_medstud_famulaturen_innere": _("Innere"),
    "ausbildung_typ_medstud_famulaturen_intensiv": _("Intensivmedizin"),
    "ausbildung_typ_medstud_famulaturen_notaufnahme": _("Notfallmedizin"),
    "ausbildung_typ_medstud_anerkennung_noetig": _(
        "<b>Nur Studierende: Eine Anerkennung als Teil eines Studienabschnitts (Pflegepraktikum/Famulatur) ist wichtig</b>"
    ),
    "ausbildung_typ_mfa": _("Medizinische/r Fachangestellte*r"),
    "ausbildung_typ_mfa_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_ota": _("Operationstechnische/r Assistent*in"),
    "ausbildung_typ_ota_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_ata": _("Anästhesietechnische/r Assistent*in"),
    "ausbildung_typ_ata_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_ergotherapie": _("Ergotherapeut*in"),
    "ausbildung_typ_ergotherapie_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_psycho": _("Psychotherapeut*in"),
    "ausbildung_typ_psycho_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_mtla": _("Medizinisch-technische/r Laboratoriumsassistent*in"),
    "ausbildung_typ_mtla_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_mta": _("Medizinisch-technische/r Assistent*in"),
    "ausbildung_typ_mta_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_notfallsani": _("Notfallsanitäter*in / Rettungsassistent*in"),
    "ausbildung_typ_notfallsani_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_sani": _("Rettungssanitäter*in/Rettungshelfer*in"),
    "ausbildung_typ_zahni": _("Zahnmedizinstudent*in"),
    "ausbildung_typ_zahni_abschnitt": _("Ausbildungsabschnitt"),
    "ausbildung_typ_kinderbetreung": _("Kinderbetreuer*in"),
    "ausbildung_typ_kinderbetreung_ausgebildet": _("Abgeschlossene Ausbildung"),
    "ausbildung_typ_kinderbetreung_vorerfahrung": _("Lediglich Erfahrungen"),
    "ausbildung_typ_sonstige": _("Sonstige"),
    "ausbildung_typ_sonstige_eintragen": _("Bitte die Qualifikationen hier eintragen"),
    "sonstige_qualifikationen": _("Weitere Qualifikationen"),
    "wunsch_ort_arzt": _("Arztpraxis/Ordination/MVZ"),
    "wunsch_ort_gesundheitsamt": _("Gesundheitsamt und sonstige Einrichtungen"),
    "wunsch_ort_krankenhaus": _("Klinikum/Spital"),
    "wunsch_ort_pflege": _("Pflegeeinrichtungen"),
    "wunsch_ort_rettungsdienst": _("Rettungsdienst"),
    "wunsch_ort_labor": _("Labor"),
    "unterkunft_gewuenscht": _("Ich brauche eine Unterkunft"),
    "wunsch_ort_apotheke": _(
        'Apotheke <em>(melde Dich auch bei <a href="http://apothekenhelfen.bphd.de/">Apothekenhelfen</a>)</em>'
    ),
    "wunsch_ort_ueberall": _("Keiner, ich helfe dort, wo ich kann"),
    "zeitliche_verfuegbarkeit": _("Zeitliche Verfügbarkeit, bis zu"),
}
fields_for_button_group = [
    "ausbildung_typ_kinderbetreung_ausgebildet_abschnitt",
    "ausbildung_typ_pflege_abschnitt",
    "ausbildung_typ_physio_abschnitt",
    "ausbildung_typ_medstud_abschnitt",
    "ausbildung_typ_mfa_abschnitt",
    "ausbildung_typ_mtla_abschnitt",
    "ausbildung_typ_mta_abschnitt",
    "ausbildung_typ_ota_abschnitt",
    "ausbildung_typ_ata_abschnitt",
    "ausbildung_typ_notfallsani_abschnitt",
    "ausbildung_typ_zahni_abschnitt",
    "ausbildung_typ_psycho_abschnitt",
    "ausbildung_typ_ergotherapie_abschnitt",
]

mindest = _("mindestens")
maxim = _("maximal")
for field in fields_for_button_group:
    if field.split("_")[-1] == "abschnitt" and "ausgebildet" not in field:
        f = str(field)
        form_labels[f + "_x_lt"] = format_lazy("{f} {extra}", f=form_labels[f], extra=maxim)
        form_labels[f + "_x_gt"] = format_lazy("{f} {extra}", f=form_labels[f], extra=mindest)


def button_group(field):
    if "empty" in field:
        return Column()
    if field in fields_for_button_group:
        return ButtonGroup(field)
    return field


# im so sorry for this... code..
def button_group_filter(field):
    if "empty" in field:
        return Column()
    if field in fields_for_button_group:
        if field.split("_")[-1] == "abschnitt" and "ausgebildet" not in field:
            return Field(
                Row(Column(ButtonGroup(field + "_x_gt"))),
                Row(Column(ButtonGroup(field + "_x_lt"))),
            )
        else:
            return ButtonGroup(field)
    return field


def ButtonGroup(field):
    return RadioButtons(
        field,
        option_label_class="btn btn-sm btn-light",
        template="input_buttongroup-any_indicator.html",
    )


def ButtonGroupBool(field):
    return RadioButtons(
        field,
        option_label_class="btn btn-sm btn-light",
        # template='input_buttongroup-any_indicator.html')
        template="input_buttongroup-egalmuss_indicator.html",
    )


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["uuid", "registration_date", "user", "is_activated"]
        labels = form_labels
        help_texts = {
            "email": _(
                "Über diese Emailadresse dürfen dich medizinische Einrichtungen kontaktieren"
            ),
            "countrycode": _("Bitte wähle ein Land aus"),
            "plz": _("bevorzugter Einsatzort als Postleitzahl"),
            # 'wunsch_ort_gesundheitsamt': _('Hotline, Teststation etc.')
        }

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields["phone_number"].required = False

        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "signup_student"
        self.helper.attrs = {"onsubmit": "disableButton()"}

        self.helper.layout = Layout(
            HTML("<h2 class='form-heading'>{}</h2>".format(_("Persönliche Informationen"))),
            Row(
                Column("name_first", css_class="form-group col-md-6 mb-0"),
                Column("name_last", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("email", css_class="form-group col-md-6 mb-0"),
                Column("phone_number", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            HTML(
                "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                    _("Über deinen Einsatz")
                )
            ),
            Row(
                Column("plz", css_class="form-group col-md-4 mb-0"),
                Column("countrycode", css_class="form-group col-md-4 mb-0"),
                Column("umkreis", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("availability_start", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            HTML("<h5 style='margin-top:20px'>{}</h5>".format(_("Wunscheinsatzort"))),
            Row(
                Column("wunsch_ort_arzt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_gesundheitsamt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_krankenhaus", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_pflege", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_rettungsdienst", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_labor", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_apotheke", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_ueberall", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("braucht_bezahlung", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("zeitliche_verfuegbarkeit", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("unterkunft_gewuenscht", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Div(
                HTML(
                    "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                        _("Berufsausbildung")
                    )
                ),
                Row(
                    *[
                        Column(
                            "ausbildung_typ_%s" % k.lower(),
                            css_class="ausbildung-checkbox form-group col-md-6 mb-0",
                            css_id="ausbildung-checkbox-%s" % AUSBILDUNGS_IDS[k],
                        )
                        for k in AUSBILDUNGS_TYPEN.keys()
                    ]
                ),
                css_id="div-berufsausbildung-dropdown",
            ),
        )

        for ausbildungstyp, felder in AUSBILDUNGS_TYPEN.items():
            if len(felder) != 0:
                if ausbildungstyp != "MEDSTUD":
                    self.helper.layout.extend(
                        [
                            Div(
                                HTML(
                                    "<h4>{}</h4>".format(
                                        _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                                    )
                                ),
                                Row(
                                    *[
                                        Column(
                                            button_group(
                                                "ausbildung_typ_%s_%s"
                                                % (ausbildungstyp.lower(), f.lower())
                                            ),
                                            css_class="form-group",
                                            css_id=f.replace("_", "-"),
                                        )
                                        for f in felder.keys()
                                        if "ausbildung_typ_medstud_abschnitt"
                                        == "ausbildung_typ_%s_%s"
                                        % (ausbildungstyp.lower(), f.lower())
                                    ]
                                ),
                                *[
                                    Column(
                                        button_group(
                                            "ausbildung_typ_%s_%s"
                                            % (ausbildungstyp.lower(), f.lower())
                                        ),
                                        css_class="form-group col-md-6 mb-0",
                                        css_id=f.replace("_", "-"),
                                    )
                                    for f in felder.keys()
                                    if "ausbildung_typ_medstud_abschnitt"
                                    != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ],
                                css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                                css_class="hidden ausbildung-addon",
                            )
                        ]
                    )
                else:
                    self.helper.layout.extend(
                        [
                            Div(
                                HTML(
                                    "<h4>{}</h4>".format(
                                        _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                                    )
                                ),
                                Row(
                                    *[
                                        Column(
                                            button_group(
                                                "ausbildung_typ_%s_%s"
                                                % (ausbildungstyp.lower(), f.lower())
                                            ),
                                            css_class="form-group",
                                            css_id=f.replace("_", "-"),
                                        )
                                        for f in felder.keys()
                                        if "ausbildung_typ_medstud_abschnitt"
                                        == "ausbildung_typ_%s_%s"
                                        % (ausbildungstyp.lower(), f.lower())
                                    ]
                                ),
                                HTML("<p>"),
                                HTML(
                                    _(
                                        "Gib hier bitte deine Vorerfahrungen oder Fachrichtung in den folgenden Feldern an:"
                                    )
                                ),
                                HTML("</p>"),
                                *[
                                    Column(
                                        button_group(
                                            "ausbildung_typ_%s_%s"
                                            % (ausbildungstyp.lower(), f.lower())
                                        ),
                                        css_class="form-group col-md-6 mb-0",
                                        css_id=f.replace("_", "-"),
                                    )
                                    for f in felder.keys()
                                    if "ausbildung_typ_medstud_abschnitt"
                                    != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ],
                                css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                                css_class="hidden ausbildung-addon",
                            )
                        ]
                    )

        self.helper.layout.extend(
            (
                "sonstige_qualifikationen",
                HTML('<hr style="margin-top: 20px; margin-bottom:30px;">'),
                HTML(
                    '<div class="registration_disclaimer">{}</div>'.format(
                        _(
                            'Wir benötigen die Information, die Sie uns zur Verfügung stellen, um Helfende und Hilfesuchende miteinander zu vernetzen. Informationen dazu, welche personenbezogenen Daten bei dem Besuch und der Nutzung der Angebote auf unserer Seite erhoben und verarbeitet werden finden Sie in unseren Datenschutzbestimmungen (Link: <a target="_blank" href="/dataprotection/">https://match4crisis.de/dataprotection/</a>).'
                        )
                    )
                ),
                Submit("submit", _("Registriere mich"), css_class="btn blue text-white btn-md",),
                HTML(
                    "<script>function disableButton() {var btn = document.getElementById('submit-id-submit'); btn.disabled = true;btn.value = 'Sending...'}</script>"
                ),
            )
        )

        logging.debug(self.helper.layout)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                mark_safe(
                    _(
                        'Diese E-mail ist bereits vergeben und eine Bestätigungsmail wurde versandt. <b><a target="_blank" href="/accounts/resend_validation_email/'
                        + email
                        + '">Klicke hier, um die Bestätigungsmail erneut zu versenden</a></b>'
                    )
                )
            )
        return email


class StudentFormAndMail(StudentForm):
    email = forms.EmailField()


class EmailForm(forms.Form):
    student_id = forms.CharField(max_length=100)
    contact_adress = forms.EmailField()


class StudentFormEditProfile(StudentForm):
    class Meta:
        model = Student
        exclude = [
            "uuid",
            "registration_date",
            "user",
            "is_activated",
            "einwilligung_agb",
            "einwilligung_datenweitergabe",
            "datenschutz_zugestimmt",
        ]
        labels = form_labels
        help_texts = {
            "email": _(
                "Über diese Emailadresse dürfen dich medizinische Einrichtungen kontaktieren"
            ),
            "countrycode": _("Bitte wähle ein Land aus"),
            "plz": _("bevorzugter Einsatzort als Postleitzahl"),
            # 'wunsch_ort_gesundheitsamt': _('Hotline, Teststation etc.')
        }

    def __init__(self, *args, **kwargs):
        super(StudentFormEditProfile, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML("<h2 class='form-heading'>{}</h2>".format(_("Persönliche Informationen"))),
            Row(
                Column("name_first", css_class="form-group col-md-6 mb-0"),
                Column("name_last", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("phone_number", css_class="form-group col-md-6 mb-0"), css_class="form-row",
            ),
            HTML(
                "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                    _("Über deinen Einsatz")
                )
            ),
            Row(
                Column("plz", css_class="form-group col-md-4 mb-0"),
                Column("countrycode", css_class="form-group col-md-4 mb-0"),
                Column("umkreis", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("availability_start", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            HTML("<h5 style='margin-top:20px'>{}</h5>".format(_("Wunscheinsatzort"))),
            Row(
                Column("wunsch_ort_arzt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_gesundheitsamt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_krankenhaus", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_pflege", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_rettungsdienst", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_labor", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_apotheke", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_ueberall", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("braucht_bezahlung", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("zeitliche_verfuegbarkeit", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("unterkunft_gewuenscht", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Div(
                HTML(
                    "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                        _("Berufsausbildung")
                    )
                ),
                Row(
                    *[
                        Column(
                            "ausbildung_typ_%s" % k.lower(),
                            css_class="ausbildung-checkbox form-group col-md-6 mb-0",
                            css_id="ausbildung-checkbox-%s" % AUSBILDUNGS_IDS[k],
                        )
                        for k in AUSBILDUNGS_TYPEN.keys()
                    ]
                ),
                css_id="div-berufsausbildung-dropdown",
            ),
            *[
                Div(
                    HTML(
                        "<h4>{}</h4>".format(
                            _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                        )
                    ),
                    Row(
                        *[
                            Column(
                                button_group(
                                    "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ),
                                css_class="form-group",
                                css_id=f.replace("_", "-"),
                            )
                            for f in felder.keys()
                            if "ausbildung_typ_medstud_abschnitt"
                            == "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                        ]
                    ),
                    Row(
                        *[
                            Column(
                                button_group(
                                    "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ),
                                css_class="form-group col-md-6 mb-0",
                                css_id=f.replace("_", "-"),
                            )
                            for f in felder.keys()
                            if "ausbildung_typ_medstud_abschnitt"
                            != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                        ]
                    ),
                    css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                    css_class="hidden ausbildung-addon",
                )
                for ausbildungstyp, felder in AUSBILDUNGS_TYPEN.items()
                if len(felder) != 0
            ],
            "sonstige_qualifikationen",
            HTML(
                '<div class="registration_disclaimer">{}</div>'.format(
                    _(
                        "Die Bereitstellung unseres Services erfolgt unentgeltlich. Mir ist bewusst, dass die Ausgestaltung des Verhältnisses zur zu vermittelnden Institution allein mich und die entsprechende Institution betrifft. Insbesondere Art und Umfang der Arbeit, eine etwaige Vergütung und vergleichbares betreffen nur mich und die entsprechende Institution. Eine Haftung des Vermittlers ist ausgeschlossen."
                    )
                )
            ),
            Submit("submit", _("Profil Aktualisieren"), css_class="btn blue text-white btn-md",),
        )


class StudentFormView(StudentForm):
    class Meta:
        model = Student
        exclude = [
            "name_first",
            "name_last",
            "registration_date",
            "user",
            "is_activated",
            "einwilligung_agb",
            "einwilligung_datenweitergabe",
            "datenschutz_zugestimmt",
        ]
        labels = form_labels
        labels["uuid"] = _("Eindeutige Kennziffer dieses Helfenden")
        labels["braucht_bezahlung"] = _("Benötigte Vergütung")
        labels["availability_start"] = _("Verfügbar Ab")
        labels["unterkunft_gewuenscht"] = _("Unterkunft Benötigt")
        labels["ausbildung_typ_pflege"] = _("Pflege")
        labels["wunsch_ort_apotheke"] = _("Apotheke")

    def __init__(self, *args, **kwargs):
        super(StudentFormView, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].disabled = True

        self.fields["uuid"].disabled = False
        self.fields["uuid"].widget.attrs["readonly"] = True
        self._hide_dropdown = (
            "-webkit-appearance:none;-moz-appearance:none;text-indent:1px;text-overflow:'';"
        )

        del self.fields["phone_number"]
        self.helper.layout = Layout(
            HTML(
                "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                    _("Allgemein")
                )
            ),
            Row(Column("uuid", css_class="form-group col-md-4 mb-0"), css_class="form-row",),
            Row(
                Column("plz", css_class="form-group col-md-4 mb-0"),
                Column(
                    "countrycode", css_class="form-group col-md-4 mb-0", style=self._hide_dropdown,
                ),
                # Column('umkreis', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column("availability_start", css_class="form-group col-md-6 mb-0"),
                Column(
                    "zeitliche_verfuegbarkeit",
                    css_class="form-group col-md-6 mb-0",
                    style=self._hide_dropdown,
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "braucht_bezahlung",
                    css_class="form-group col-md-6 mb-0",
                    style=self._hide_dropdown,
                ),
                Column("unterkunft_gewuenscht", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Div(
                HTML(
                    "<hr style='margin-top: 30px; margin-bottom:30px;'><h2 class='form-heading'>{}</h2>".format(
                        _("Berufsausbildung")
                    )
                ),
                Row(
                    *[
                        Column(
                            "ausbildung_typ_%s" % k.lower(),
                            css_class="ausbildung-checkbox form-group col-md-6 mb-0",
                            css_id="ausbildung-checkbox-%s" % AUSBILDUNGS_IDS[k],
                        )
                        for k in AUSBILDUNGS_TYPEN.keys()
                    ]
                ),
                css_id="div-berufsausbildung-dropdown",
            ),
            *[
                Div(
                    HTML(
                        "<h4>{}</h4>".format(
                            _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                        )
                    ),
                    Row(
                        *[
                            Column(
                                button_group(
                                    "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ),
                                css_class="form-group",
                                css_id=f.replace("_", "-"),
                            )
                            for f in felder.keys()
                            if "ausbildung_typ_medstud_abschnitt"
                            == "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                        ]
                    ),
                    Row(
                        *[
                            Column(
                                button_group(
                                    "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ),
                                css_class="form-group col-md-6 mb-0",
                                css_id=f.replace("_", "-"),
                            )
                            for f in felder.keys()
                            if "ausbildung_typ_medstud_abschnitt"
                            != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                        ]
                    ),
                    css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                    css_class="hidden ausbildung-addon",
                )
                for ausbildungstyp, felder in AUSBILDUNGS_TYPEN.items()
                if len(felder) != 0
            ],
            "sonstige_qualifikationen",
            HTML("<h5 style='margin-top:20px'>{}</h5>".format(_("Wunscheinsatzort"))),
            Row(
                Column("wunsch_ort_arzt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_gesundheitsamt", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_krankenhaus", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_pflege", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_rettungsdienst", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_labor", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_apotheke", css_class="form-group col-md-6 mb-0"),
                Column("wunsch_ort_ueberall", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
        )


class EmailToSendForm(forms.ModelForm):
    class Meta:
        model = EmailToSend
        fields = ["subject", "message"]
        labels = {"subject": _("Betreff"), "message": _("Nachrichtentext")}
        help_texts = {}

    def clean_message(self):
        message = self.cleaned_data["message"]
        initial_message = self.initial["message"]
        if "".join(str(message).split()) == "".join(str(initial_message).split()):
            raise ValidationError(_("Bitte personalisiere diesen Text"), code="invalid")
        return message

    def __init__(self, *args, **kwargs):
        super(EmailToSendForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            HTML("<h2 class='form-heading'>{}</h2>".format(_("Persönliche Informationen"))),
            "subject",
            Div(
                HTML(
                    _(
                        "Bitte schreiben Sie in diese Mail an die Helfenden kurze Informationen zur geplanten Tätigkeit:\n\n"
                        "<ul>"
                        "<li>zeitlicher Umfang,</li>"
                        "<li>Aufgabengebiet/Abteilung</li>"
                        "<li>Vergütung / Modalitäten</li>"
                        "<li>Arbeitsvertrag / Versicherungsverhältnis</li></ul>"
                        "So können die Helfenden schneller sehen, ob diese Stelle zu Ihnen passt, sparen sich "
                        "Nachfragen bei Ihnen und können zügiger zu- oder absagen.\n\n"
                    )
                ),
                HTML(
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'
                    '<span aria-hidden="true">&times;</span>'
                    "</button>"
                ),
                css_class="alert alert-info alert-dismissable",
                role="alert",
            ),
            "message",
        )


def get_form_helper_filter():
    helper = FormHelper()
    helper.form_id = "id-exampleForm"
    helper.form_class = "blueForms"
    helper.form_method = "get"

    helper.form_action = "submit_survey"
    helper.form_style = "inline"
    helper.layout = Layout(
        Div(
            Row(
                *[
                    Column(
                        "ausbildung_typ_%s" % k.lower(),
                        css_class="ausbildung-checkbox form-group col-md-6 mb-0",
                        css_id="ausbildung-checkbox-%s" % AUSBILDUNGS_IDS[k],
                    )
                    for k in AUSBILDUNGS_TYPEN.keys()
                ]
            ),
            css_id="div-berufsausbildung-dropdown",
        )
    )

    for ausbildungstyp, felder in AUSBILDUNGS_TYPEN.items():
        if len(felder) != 0:
            if ausbildungstyp != "MEDSTUD":
                helper.layout.extend(
                    [
                        Div(
                            HTML(
                                "<hr><h5>Zusätzliche Filter zu {}</h5>".format(
                                    _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                                )
                            ),
                            Row(
                                *[
                                    Column(
                                        button_group_filter(
                                            "ausbildung_typ_%s_%s"
                                            % (ausbildungstyp.lower(), f.lower())
                                        ),
                                        css_class="form-group",
                                        css_id=f.replace("_", "-"),
                                    )
                                    for f in felder.keys()
                                    if "ausbildung_typ_medstud_abschnitt"
                                    == "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ]
                            ),
                            *[
                                Column(
                                    button_group_filter(
                                        "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                    ),
                                    css_class="form-group col-md-6 mb-0",
                                    css_id=f.replace("_", "-"),
                                )
                                for f in felder.keys()
                                if "ausbildung_typ_medstud_abschnitt"
                                != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                            ],
                            css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                            css_class="hidden ausbildung-addon",
                        )
                    ]
                )
            else:
                helper.layout.extend(
                    [
                        Div(
                            HTML(
                                "<hr><h5>Zusätzliche Filter zu {}</h5>".format(
                                    _(form_labels["ausbildung_typ_%s" % ausbildungstyp.lower()])
                                )
                            ),
                            Row(
                                *[
                                    Column(
                                        button_group_filter(
                                            "ausbildung_typ_%s_%s"
                                            % (ausbildungstyp.lower(), f.lower())
                                        ),
                                        css_class="form-group",
                                        css_id=f.replace("_", "-"),
                                    )
                                    for f in felder.keys()
                                    if "ausbildung_typ_medstud_abschnitt"
                                    == "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                ]
                            ),
                            HTML("<p>"),
                            HTML(
                                _(
                                    "In welchen der folgenden Bereiche sind Vorerfahrungen notwendig?"
                                )
                            ),
                            HTML("</p>"),
                            *[
                                Column(
                                    button_group_filter(
                                        "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                                    ),
                                    css_class="form-group col-md-6 mb-0",
                                    css_id=f.replace("_", "-"),
                                )
                                for f in felder.keys()
                                if "ausbildung_typ_medstud_abschnitt"
                                != "ausbildung_typ_%s_%s" % (ausbildungstyp.lower(), f.lower())
                            ],
                            css_id="div-ausbildung-%s" % AUSBILDUNGS_IDS[ausbildungstyp],
                            css_class="hidden ausbildung-addon",
                        )
                    ]
                )

    helper.form_tag = False
    helper.layout.extend(
        [
            HTML("<hr><h5>"),
            HTML(_(" Welche Infos über die zu vergebende Stelle sind schon bekannt?")),
            HTML("</h5>"),
            "availability_start",
            Row(
                Column(InlineRadios("braucht_bezahlung")),
                Column(InlineRadios("unterkunft_gewuenscht")),
            ),
        ]
    )
    return helper
