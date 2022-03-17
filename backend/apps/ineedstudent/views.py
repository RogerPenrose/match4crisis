from datetime import datetime
from functools import lru_cache

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.gzip import gzip_page
import django_tables2 as tables
from django_tables2 import TemplateColumn

from apps.accounts.decorator import hospital_required
from apps.iamstudent.models import EmailToHospital, Student
from apps.ineedstudent.forms import EmailToHospitalForm
from apps.ineedstudent.models import Hospital
from apps.mapview.utils import haversine, plzs
from apps.mapview.views import get_ttl_hash

from .forms import PostingForm
from .tables import ContactedTable


class StudentTable(tables.Table):
    info = TemplateColumn(template_name="info_button.html")
    checkbox = TemplateColumn(template_name="checkbox_studenttable.html")

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap4.html"
        exclude = ["uuid", "registration_date", "id"]
        fields = ["user"]


# Should be safe against BREACH attack because we don't have user input in reponse body
@gzip_page
def hospital_overview(request):
    locations_and_number = prepare_hospitals(ttl_hash=get_ttl_hash(60))
    template = loader.get_template("map_hospitals.html")
    context = {
        "locations": list(locations_and_number.values()),
        "mapbox_token": settings.MAPBOX_TOKEN,
    }
    return HttpResponse(template.render(context, request))


@lru_cache(maxsize=1)
def prepare_hospitals(ttl_hash=None):
    hospitals = Hospital.objects.filter(
        user__validated_email=True, is_approved=True, appears_in_map=True
    )
    locations_and_number = {}
    for hospital in hospitals:
        if len(hospital.sonstige_infos) != 0:
            cc = hospital.countrycode
            plz = hospital.plz
            key = cc + "_" + plz
            if key in locations_and_number:
                locations_and_number[key]["count"] += 1
                locations_and_number[key]["uuid"] = None
            else:
                lat, lon, ort = plzs[cc][plz]
                locations_and_number[key] = {
                    "uuid": hospital.uuid,
                    "countrycode": cc,
                    "plz": plz,
                    "count": 1,
                    "lat": lat,
                    "lon": lon,
                    "ort": ort,
                }
    return locations_and_number


@login_required
def hospital_list(request, countrycode, plz):

    if countrycode not in plzs or plz not in plzs[countrycode]:
        # TODO: niceren error werfen # noqa: T003
        return HttpResponse(
            "Postleitzahl: " + plz + " ist keine valide Postleitzahl in " + countrycode
        )

    lat, lon, ort = plzs[countrycode][plz]

    table = HospitalTable(
        Hospital.objects.filter(
            user__validated_email=True, is_approved=True, plz=plz, appears_in_map=True
        )
    )
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    context = {"countrycode": countrycode, "plz": plz, "ort": ort, "table": table}

    return render(request, "list_hospitals_by_plz.html", context)


class HospitalTable(tables.Table):
    info = TemplateColumn(template_name="info_button.html")

    class Meta:
        model = Hospital
        template_name = "django_tables2/bootstrap4.html"
        fields = ["firmenname", "ansprechpartner"]
        exclude = ["uuid", "registration_date", "id"]


class ApprovalHospitalTable(HospitalTable):
    info = TemplateColumn(template_name="info_button.html")
    status = TemplateColumn(template_name="approval_button.html")
    delete = TemplateColumn(template_name="delete_button.html")

    class Meta:
        model = Hospital
        template_name = "django_tables2/bootstrap4.html"
        fields = [
            "firmenname",
            "ansprechpartner",
            "user",
            "telefon",
            "plz",
            "user__validated_email",
            "approval_date",
            "approved_by",
        ]
        exclude = ["uuid", "id", "registration_date"]


@login_required
def hospital_view(request, uuid):
    h = Hospital.objects.filter(uuid=uuid)[0]
    initial = {
        "subject": _("Neues Hilfsangebot"),
        "message": _(
            "Hallo, ich habe ihr Gesuche auf der Plattform match4crisis gesehen und bin für die Stelle qualifiziert.\nIch bin...\nIch möchte helfen in dem..."
        ),
    }

    email_form = EmailToHospitalForm(initial=initial)

    if request.POST and request.user.is_student and request.user.validated_email:
        s = request.user.student

        email_form = EmailToHospitalForm(request.POST, initial=initial)

        if email_form.is_valid():
            start_text = _(
                "Hallo %s,\n\nSie haben über unsere Plattform match4crisis von %s (%s) eine Antwort auf Ihre Anzeige bekommen.\n"
                "Falls Sie keine Anfragen mehr bekommen möchten, deaktivieren Sie Ihre "
                "Anzeige im Profil online.\n\n"
                % (h.ansprechpartner, s.name_first, request.user.email)
            )
            message = (
                start_text
                + "===============================================\n\n"
                + email_form.cleaned_data["message"]
                + "\n\n===============================================\n\n"
                + "Mit freundlichen Grüßen,\nIhr match4crisis Team"
            )
            emailtohospital = EmailToHospital.objects.create(
                student=s,
                hospital=h,
                message=email_form.cleaned_data["message"],
                subject=email_form.cleaned_data["subject"],
            )

            email = EmailMessage(
                subject="[match4crisis] " + email_form.cleaned_data["subject"],
                body=message,
                from_email=settings.NOREPLY_MAIL,
                to=[h.user.email],
            )
            email.send()
            emailtohospital.send_date = datetime.now()
            emailtohospital.save()

            return render(request, "hospital_contacted.html")

    lat1, lon1, ort1 = plzs[h.countrycode][h.plz]

    context = {
        "hospital": h,
        "uuid": h.uuid,
        "ort": ort1,
        "hospital": h,
        "mail": h.user.username,
    }

    if request.user.is_student:
        s = Student.objects.get(user=request.user)
        lat2, lon2, context["student_ort"] = plzs[s.countrycode][s.plz]
        context["distance"] = int(haversine(lon1, lat1, lon2, lat2))
        context["plz_student"] = s.plz

    context["email_form"] = email_form

    return render(request, "hospital_view.html", context)


@login_required
@hospital_required
def change_posting(request):
    if request.method == "POST":
        anzeige_form = PostingForm(request.POST, instance=request.user.hospital)

        if anzeige_form.is_valid():
            anzeige_form.save()
            messages.add_message(
                request, messages.INFO, _("Deine Anzeige wurde erfolgreich aktualisiert."),
            )

    else:
        anzeige_form = PostingForm(instance=request.user.hospital)

    context = {"anzeige_form": anzeige_form}
    return render(request, "change_posting.html", context)


@login_required
@hospital_required
def hospital_dashboard(request):

    # tabelle kontaktierter Studis
    values = ["student", "registration_date", "message", "subject"]
    qs = request.user.hospital.emailtosend_set.all().values(
        *values, is_activated=models.F("student__is_activated")
    )
    kontaktiert_table = ContactedTable(qs)

    context = {
        "already_contacted": len(qs) > 0,
        "has_posting": request.user.hospital.appears_in_map,
        "posting_text": request.user.hospital.sonstige_infos,
        "kontaktiert_table": kontaktiert_table,
    }
    return render(request, "hospital_dashboard.html", context)
