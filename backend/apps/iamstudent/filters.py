import django.forms as forms
from django.utils.translation import gettext_lazy as _
import django_filters as filters

from .forms import get_form_helper_filter
from .models import AUSBILDUNGS_TYPEN_COLUMNS, BEZAHLUNG_CHOICES_Filter, Student


class StudentJobRequirementsFilter(filters.FilterSet):

    ausbildung_typ_medstud_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_medstud_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_medstud_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_medstud_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_mfa_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_mfa_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_mfa_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_mfa_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_mta_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_mta_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_mta_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_mta_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_ota_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_ota_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_ota_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_ota_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_ata_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_ata_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_ata_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_ata_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_mtla_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_mtla_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_mtla_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_mtla_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_notfallsani_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_notfallsani_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_notfallsani_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_notfallsani_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_physio_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_physio_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_physio_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_physio_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_ergotherapie_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_ergotherapie_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_ergotherapie_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_ergotherapie_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_psycho_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_psycho_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_psycho_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_psycho_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_pflege_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_pflege_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_pflege_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_pflege_abschnitt", lookup_expr="lte"
    )

    ausbildung_typ_zahni_abschnitt_x_gt = filters.NumberFilter(
        "ausbildung_typ_zahni_abschnitt", lookup_expr="gte"
    )
    ausbildung_typ_zahni_abschnitt_x_lt = filters.NumberFilter(
        "ausbildung_typ_zahni_abschnitt", lookup_expr="lte"
    )

    braucht_bezahlung = filters.ChoiceFilter(
        field_name="braucht_bezahlung",
        method="not_equal",
        choices=BEZAHLUNG_CHOICES_Filter,
        widget=forms.RadioSelect,
    )
    availability_start = filters.DateFilter(field_name="availability_start", lookup_expr="lte",)
    unterkunft_gewuenscht = filters.ChoiceFilter(
        field_name="unterkunft_gewuenscht", choices=[(False, _("nein"))], widget=forms.RadioSelect,
    )

    unterkunft_gewuenscht.field.empty_label = _("ist möglich")
    braucht_bezahlung.field.empty_label = _(
        "Wir können zwar Vergütung anbieten, nehmen aber auch Unterstützung von Helfenden an, "
        "die keine Bezahlung wünschen."
    )

    class Meta:
        model = Student
        fields = AUSBILDUNGS_TYPEN_COLUMNS.copy()

        for f in [
            "ausbildung_typ_medstud_famulaturen_anaesthesie",
            "ausbildung_typ_medstud_famulaturen_allgemeinmedizin",
            "ausbildung_typ_medstud_famulaturen_chirurgie",
            "ausbildung_typ_medstud_famulaturen_innere",
            "ausbildung_typ_medstud_famulaturen_intensiv",
            "ausbildung_typ_medstud_famulaturen_notaufnahme",
            "ausbildung_typ_medstud_anerkennung_noetig",
            "ausbildung_typ_kinderbetreung_ausgebildet_abschnitt",
        ]:
            fields.append(f)

    def not_equal(self, queryset, name, value):
        lookup = "__".join([name, "exact"])
        if value == "1":  # nur bezahlung
            return queryset.exclude(**{lookup: 3})
        else:  # nur ohne Vergütung
            return queryset.exclude(**{lookup: 1})

    def __init__(self, *args, **kwargs):
        if "display_version" not in kwargs.keys():
            display_version = False
        else:
            display_version = True
            del kwargs["display_version"]

        super(StudentJobRequirementsFilter, self).__init__(*args, **kwargs)
        from .forms import form_labels

        self.Meta.labels = form_labels
        self.Meta.labels["unterkunft_gewuenscht"] = _("Kann eine Unterkunft angeboten werden?")
        self.Meta.labels["availability_start"] = _(
            "Die Helfenden sollten mindestens verfügbar sein ab dem"
        )
        self.Meta.labels["braucht_bezahlung"] = _("Vergütungsmodell für Helfende")

        THREE_CHOICES = [("true", _("notwendig"))]

        if display_version:
            for a_field in self.form.fields.keys():
                approved = self.form.fields[a_field]

                if type(approved) is forms.NullBooleanField:
                    self.form.fields[a_field] = forms.MultipleChoiceField(
                        choices=THREE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple,
                    )
                if type(approved) is forms.DecimalField:
                    basename = a_field.split("_x_")[0]
                    CHOICES = self.Meta.model._meta._forward_fields_map[basename].choices
                    from copy import deepcopy

                    if a_field.split("_x_")[1] == "gt":
                        CHOICES_GT = list(deepcopy(CHOICES))
                        CHOICES_GT[0] = ("", _("Egal"))
                        self.form.fields[a_field] = forms.TypedChoiceField(
                            choices=CHOICES_GT, required=False
                        )
                        self.form.fields[a_field].initial = 0
                    else:
                        CHOICES_LT = list(deepcopy(CHOICES))
                        CHOICES_LT[0] = ("", _("Egal"))
                        self.form.fields[a_field] = forms.TypedChoiceField(
                            choices=CHOICES_LT, required=False
                        )
                        self.form.fields[a_field].initial = 10

                if a_field in form_labels.keys():
                    self.form.fields[a_field].label = form_labels[a_field]

            self.form_helper = get_form_helper_filter()
