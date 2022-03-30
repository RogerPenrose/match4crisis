from datetime import datetime
import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.text import format_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from apps.iofferhelp.forms import HelperCreationForm, HelperPreferencesForm
from apps.ineedhelp.forms import RefugeeCreationForm, RefugeePreferencesForm
from apps.accounts.forms import CommonPreferencesForm, CustomAuthenticationForm
from rest_framework.views import APIView

from apps.accounts.utils import send_password_set_email
#from apps.iofferhelp.forms import HelperForm, HelperFormAndMail, HelperFormEditProfile
from apps.iofferhelp.models import Helper
#from apps.iofferhelp.views import send_mails_for
from apps.iamorganisation.forms import (
    OrganisationFormInfoCreate,
    OrganisationFormInfoSignUp,
    OrganisationPreferencesForm,
)
from apps.iamorganisation.models import Organisation
from apps.ineedhelp.models import Refugee
from apps.offers.models import GenericOffer, OFFER_MODELS
#from apps.iamorganisation.views import ApprovalOrganisationTable

from .decorator import organisationRequired, helperRequired
from .models import User

logger = logging.getLogger(__name__)


@login_required
@staff_member_required
def staff_profile(request):
    return render(request, "staff_profile.html", {})


def signup_refugee(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        logger.info("Refugee Signup request", extra={"request": request})
        form = RefugeeCreationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/ineedhelp/thanks")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RefugeeCreationForm()

    return render(request, "signup_refugee.html", {"form": form})



def signup_helper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        logger.info("Helper Signup request", extra={"request": request})
        form = HelperCreationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            user, helper = form.save()
            # If the user got here through the /iofferhelp/choose_help page, get the chosen help data from the request session
            if('chosenHelp' in request.session):
                chosenHelp = request.session['chosenHelp'].items()
                for offerType, chosen in chosenHelp:
                    if chosen:
                        # Create a new incomplete offer of this type
                        genericOffer = GenericOffer(offerType=offerType, userId=user, active=False, incomplete=True)
                        genericOffer.save()
                        specOffer = OFFER_MODELS[offerType](genericOffer=genericOffer)
                        specOffer.save()

            return HttpResponseRedirect("/iofferhelp/thanks")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HelperCreationForm()

    return render(request, "signup_helper.html", {"form": form})



def signup_organisation(request):
    if request.method == "POST":
        logger.info("Organisation registration request", extra={"request": request})
        form_info = OrganisationFormInfoSignUp(request.POST)

        if form_info.is_valid():
            user, organisation = register_organisation_in_db(request, form_info.cleaned_data)
            send_password_set_email(
                email=form_info.cleaned_data["email"],
                host=request.META["HTTP_HOST"],
                template="registration/password_set_email_organisation.html",
                subject_template="registration/password_reset_email_subject.txt",
            )
            return HttpResponseRedirect("/iamorganisation/thanks_organisation")
        #else: raise Exception(form_info.errors)

            # plz = form_info.cleaned_data['plz']
            # countrycode = form_info.cleaned_data['countrycode']
            # distance = 0
            # login(request, user)
            # return HttpResponseRedirect('/iamorganisation/helpers/%s/%s/%s'%(countrycode,plz,distance))

    else:
        form_info = OrganisationFormInfoSignUp()
        # form_user = OrganisationSignUpForm()
    form_info.helper.form_tag = False
    return render(request, "signup_organisation.html", {"form_info": form_info})


@transaction.atomic
def register_organisation_in_db(request, formData):

    pwd = formData["password1"]
    user = User.objects.create(email=formData["email"], isOrganisation=True)
    user.set_password(pwd)
    user.phoneNumber = formData["phoneNumber"]
    print("Saving User")
    user.save()

    organisation = Organisation.objects.create(user=user)
    organisation = OrganisationFormInfoCreate(request.POST, instance=organisation)
    print("Saving Organisation")
    organisation.save()
    return user, organisation


@login_required
def login_redirect(request):
    user = request.user

    if user.isHelper:
        return HttpResponseRedirect("/iofferhelp/helper_dashboard")

    elif user.isRefugee:
        return HttpResponseRedirect("/ineedhelp/refugee_dashboard")

    elif user.isOrganisation:
        return HttpResponseRedirect("/iamorganisation/organisation_dashboard")

    elif user.is_staff:
        return HttpResponseRedirect("approve_organisations")

    else:
        # TODO: throw 404  # noqa: T003
        logger.warning(
            "User is unknown type, login redirect not possible", extra={"request": request},
        )
        HttpResponse("Something wrong in database")

"""
@login_required
@helperRequired
def edit_helper_profile(request):
    helper = request.user.helper

    if request.method == "POST":
        logger.info("Update Helper Profile", extra={"request": request})
        form = HelperFormEditProfile(request.POST or None, instance=helper, prefix="infos")

        if form.is_valid():
            messages.success(
                request, _("Deine Daten wurden erfolgreich geändert!"), extra_tags="alert-success",
            )
            form.save()

    else:
        form = HelperFormEditProfile(instance=helper, prefix="infos")

    return render(
        request, "helper_edit.html", {"form": form, "is_activated": helper.is_activated},
    )
"""

"""@login_required
@organisationRequired
def edit_organisation_profile(request):
    organisation = request.user.organisation

    if request.method == "POST":
        logger.info("Update Organisation Profile", extra={"request": request})
        form = OrganisationFormEditProfile(request.POST or None, instance=organisation, prefix="infos")

        if form.is_valid():
            messages.success(
                request, _("Deine Daten wurden erfolgreich geändert!"), extra_tags="alert-success",
            )
            form.save()
        else:
            messages.info(
                request,
                _("Deine Daten wurden nicht erfolgreich geändert!"),
                extra_tags="alert-warning",
            )

    else:
        form = OrganisationFormEditProfile(instance=organisation, prefix="infos")

    return render(request, "organisation_edit.html", {"form": form})"""

"""
@login_required
@staff_member_required
def approve_organisations(request):
    table_approved = ApprovalOrganisationTable(Organisation.objects.filter(is_approved=True))
    table_approved.prefix = "approved"
    table_approved.paginate(page=request.GET.get(table_approved.prefix + "page", 1), per_page=5)

    table_unapproved = ApprovalOrganisationTable(Organisation.objects.filter(is_approved=False))
    table_unapproved.prefix = "unapproved"
    table_unapproved.paginate(page=request.GET.get(table_unapproved.prefix + "page", 1), per_page=5)

    return render(
        request,
        "approve_organisations.html",
        {"table_approved": table_approved, "table_unapproved": table_unapproved},
    )


@login_required
@staff_member_required
def change_organisation_approval(request, uuid):

    h = Organisation.objects.get(uuid=uuid)
    logger.info(
        "Set Organisation %s approval to %s", uuid, (not h.is_approved), extra={"request": request},
    )

    if not h.is_approved:
        h.is_approved = True
        h.approval_date = datetime.now()
        h.approved_by = request.user
    else:
        h.is_approved = False
        h.approval_date = None
        h.approved_by = None
    h.save()

    if h.is_approved:
        send_mails_for(h)

    return HttpResponseRedirect("/accounts/approve_organisations")
"""

@login_required
@staff_member_required
def delete_organisation(request, uuid):
    h = Organisation.objects.get(uuid=uuid)
    logger.info(
        "Delete Organisation %s by %s", uuid, request.user, extra={"request": request},
    )
    name = h.user
    h.delete()
    text = format_lazy(_("Du hast die Institution mit user '{name}' gelöscht."), name=name)
    messages.add_message(request, messages.INFO, text)
    return HttpResponseRedirect("/accounts/approve_organisations")


@login_required
def delete_me(request):
    user = request.user
    logout(request)
    user.delete()
    return render(request, "deleted_user.html")


@login_required
def delete_me_ask(request):
    return render(request, "deleted_user_ask.html")


@login_required
def validate_email(request):
    if not request.user.validated_email:
        request.user.validated_email = True
        request.user.email_validation_date = datetime.now()
        request.user.save()
    return HttpResponseRedirect("login_redirect")


def resend_validation_email(request, email):
    if request.user.is_anonymous:
        if not User.objects.get(email=email).validated_email:
            send_password_set_email(
                email=email,
                host=request.META["HTTP_HOST"],
                template="registration/password_set_email_.html",
                subject_template="registration/password_reset_email_subject.txt",
            )
            return HttpResponseRedirect("/accounts/password_reset/done")
    return HttpResponseRedirect("/")


class UserCountView(APIView):
    """
    A view that returns the count of active users.

    Source: https://stackoverflow.com/questions/25151586/django-rest-framework-retrieving-object-count-from-a-model
    """

    def get(self, request, format=None):  # noqa: A002
        supporter_count = User.objects.filter(
            isHelper__exact=True, validated_email__exact=True
        ).count()
        facility_count = User.objects.filter(
            isOrganisation__exact=True, validated_email__exact=True
        ).count()
        content = {"user_count": supporter_count, "facility_count": facility_count}
        return JsonResponse(content)


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def post(self, request, *args, **kwargs):
        print("Login Attempt", request.POST["email"])
        logger.info("Login Attempt (%s)", request.POST["email"])
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("Login successful", form.cleaned_data["email"])
        logger.info("Login successful (%s)", form.cleaned_data["email"])
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Login failure", getattr(form.data, "email", ""))
        logger.warning("Login failure (%s)", getattr(form.data, "email", ""))
        return super().form_invalid(form)


@login_required
@helperRequired
def change_activation_ask(request):
    return render(
        request, "change_activation_ask.html", {"is_activated": request.user.helper.is_activated},
    )


@login_required
@helperRequired
def change_activation(request):
    s = request.user.helper
    status = s.is_activated
    s.is_activated = not s.is_activated
    s.save()
    if status:
        messages.add_message(
            request,
            messages.INFO,
            _(
                "Du hast dein Profil erfolgreich deaktiviert, du kannst nun keine Anfragen mehr von Hilfesuchenden bekommen."
            ),
        )
    else:
        messages.add_message(
            request,
            messages.INFO,
            _(
                "Du hast dein Profil erfolgreich aktiviert, du kannst nun wieder von Hilfesuchenden kontaktiert werden."
            ),
        )
    return HttpResponseRedirect("profile_helper")


class DashboardView(TemplateView):
    pass

@login_required
def preferences(request):
    user = request.user
    if(user.isRefugee):
        userTypeClass = Refugee
        userTypeForm = RefugeePreferencesForm
    elif(user.isOrganisation):
        userTypeClass = Organisation
        userTypeForm = OrganisationPreferencesForm
    else:
        userTypeClass = Helper
        userTypeForm = HelperPreferencesForm

    specificAccount = userTypeClass.objects.get(user=user)
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            logger.info("Preferences edit request", extra={"request": request})
            comPrefForm = CommonPreferencesForm(request.POST, instance=user)
            specPrefForm = userTypeForm(request.POST, instance = specificAccount)

            if comPrefForm.is_valid() and specPrefForm.is_valid():
                user = comPrefForm.save()
                specificAccount = specPrefForm.save()
                return HttpResponseRedirect("/accounts/preferences")
        else:
            comPrefForm = CommonPreferencesForm(instance=user)
            specPrefForm = userTypeForm(instance = specificAccount)
        return render(request, "preferences.html", {"comPrefForm": comPrefForm, "specPrefForm": specPrefForm})
    else:
        return HttpResponse("User is anonymous or not active")