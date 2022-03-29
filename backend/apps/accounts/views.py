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
from apps.iofferhelp.forms import HelperCreationForm
from apps.ineedhelp.forms import RefugeeCreationForm
from apps.accounts.forms import CustomAuthenticationForm
from rest_framework.views import APIView

from apps.accounts.utils import send_password_set_email
#from apps.iofferhelp.forms import HelperForm, HelperFormAndMail, HelperFormEditProfile
from apps.iofferhelp.models import Helper
#from apps.iofferhelp.views import send_mails_for
from apps.iamorganisation.forms import (
    OrganisationFormEditProfile,
    OrganisationFormInfoCreate,
    OrganisationFormInfoSignUp,
)
from apps.iamorganisation.models import Organisation
#from apps.iamorganisation.views import ApprovalOrganisationTable

from .decorator import organisationRequired, helperRequired
from .models import User

logger = logging.getLogger(__name__)


@login_required
@staff_member_required
def staff_profile(request):
    return render(request, "staff_profile.html", {})


def refugee_signup(request):
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

    return render(request, "refugee_signup.html", {"form": form})



def helper_signup(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        logger.info("Helper Signup request", extra={"request": request})
        form = HelperCreationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/iofferhelp/thanks")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HelperCreationForm()

    return render(request, "helper_signup.html", {"form": form})



def organisation_signup(request):
    if request.method == "POST":
        logger.info("Organisation registration request", extra={"request": request})
        form_info = OrganisationFormInfoSignUp(request.POST)

        if form_info.is_valid():
            user, organisation = register_organisation_in_db(request, form_info.cleaned_data["email"], form_info.cleaned_data["phoneNumber"])
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
        form_info = OrganisationFormInfoSignUp(
            initial={"sonstige_infos": "Liebe Studis,\n\nwir suchen euch weil ...\n\nBeste Grüße! "}
        )
        # form_user = OrganisationSignUpForm()
    form_info.helper.form_tag = False
    return render(request, "organisation_signup.html", {"form_info": form_info})


@transaction.atomic
def register_organisation_in_db(request, m, phoneNumber):

    pwd = User.objects.make_random_password()
    user = User.objects.create(email=m, isOrganisation=True)
    user.set_password(pwd)
    user.phoneNumber = phoneNumber
    print("Saving User")
    user.save()

    organisation = Organisation.objects.create(user=user)
    organisation = OrganisationFormInfoCreate(request.POST, instance=organisation)
    print("Saving Organisation")
    organisation.save()
    return user, organisation


@login_required
def profile_redirect(request):
    user = request.user

    if user.isHelper:
        return HttpResponseRedirect("profile_helper")

    elif user.isOrganisation:
        return HttpResponseRedirect("profile_organisation")

    elif user.isRefugee:
        return HttpResponseRedirect("profile_refugee")

    elif user.is_staff:
        return HttpResponseRedirect("profile_staff")

    else:
        # TODO: throw 404  # noqa: T003
        logger.warning(
            "User is unknown type, profile redirect not possible", extra={"request": request},
        )
        HttpResponse("Something wrong in database")


@login_required
def login_redirect(request):
    user = request.user

    if user.isHelper:
        return HttpResponseRedirect("/accounts/profile_helper")

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

@login_required
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

    return render(request, "organisation_edit.html", {"form": form})

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


"""def switch_newsletter(nl, user, request, post=None, get=None):
    nl_state = nl.sending_state()

    if nl_state == NewsletterState.BEING_EDITED:
        # an edit was made
        if post is not None:
            form = NewsletterEditForm(post, uuid=nl.uuid, instance=nl)

            if form.is_valid():
                form.save()
                nl.edit_meta_data(user)
                nl.save()
                messages.add_message(request, messages.INFO, _("Bearbeitungen gespeichert."))
                return switch_newsletter(nl, user, request, post=None, get=None)

        elif get is not None:
            # wants to freeze the form for review
            if "freezeNewsletter" in get:
                nl.freeze(user)
                nl.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    _(
                        "Der Newsletter kann nun nicht mehr editiert werden. Andere Leute können ihn approven."
                    ),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)
            else:
                # the form is a virgin
                form = NewsletterEditForm(uuid=nl.uuid, instance=nl)
        else:
            form = NewsletterEditForm(uuid=nl.uuid, instance=nl)

    elif nl_state == NewsletterState.UNDER_APPROVAL:
        if get is not None:
            if "unFreezeNewsletter" in get:
                nl.unfreeze()
                nl.save()
                messages.add_message(
                    request, messages.INFO, _("Der Newsletter kann wieder bearbeitet werden."),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)
            elif "approveNewsletter" in get:
                # TODO: check that author cannot approve # noqa: T003
                nl.approve_from(user)
                nl.save()
                messages.add_message(
                    request,
                    messages.WARNING,
                    format_lazy(
                        _(
                            "Noch ist deine Zustimmung UNGÜLTIG. Du musst den Validierungslink in der dir gesendeten Mail ({mail}) anklicken."
                        ),
                        mail=user.email,
                    ),
                )
                approval = LetterApprovedBy.objects.get(newsletter=nl, user=request.user)
                nl.send_approval_mail(approval, host=request.META["HTTP_HOST"])
                switch_newsletter(nl, user, request, post=None, get=None)

        form = NewsletterViewForm(instance=nl)

    elif nl_state == NewsletterState.READY_TO_SEND:
        if get is not None:
            if "sendNewsletter" in get:
                nl.send(user)
                nl.save()
                messages.add_message(request, messages.INFO, _("Der Newsletter wurde versendet."))
                switch_newsletter(nl, user, request)
            if "unFreezeNewsletter" in get:
                nl.unfreeze()
                nl.save()
                messages.add_message(
                    request, messages.INFO, _("Der Newsletter kann wieder bearbeitet werden."),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)

        form = NewsletterViewForm(instance=nl)

    elif nl_state == NewsletterState.SENT:
        form = NewsletterViewForm(instance=nl)
    else:
        from django.http import Http404

        raise Http404

    return form, nl


@login_required
@staff_member_required
def view_newsletter(request, uuid):
    # 404 if not there?
    nl = Newsletter.objects.get(uuid=uuid)

    if request.method == "GET" and "email" in request.GET:
        email = request.GET.get("email")
        nl.send_testmail_to(email)
        messages.add_message(
            request, messages.INFO, _("Eine Test Email wurde an %s versendet." % email)
        )

    post = request.POST if request.method == "POST" else None
    get = request.GET if request.method == "GET" else None

    form, nl = switch_newsletter(nl, request.user, request, post=post, get=get)

    # special view if person was the freezer

    context = {
        "form": form,
        "uuid": uuid,
        "newsletter_state": nl.sending_state(),
        "state_enum": NewsletterState,
        "mail_form": TestMailForm(),
        "already_approved_by_this_user": nl.has_been_approved_by(request.user),
        "required_approvals": nl.required_approvals(),
        "frozen_by": nl.frozen_by,
        "sent_by": nl.sent_by,
        "send_date": nl.send_date,
        "approvers": ", ".join([a.user.email for a in nl.letterapprovedby_set.all()]),
    }

    return render(request, "newsletter_edit.html", context)


@login_required
@staff_member_required
def new_newsletter(request):
    newsletter = Newsletter.objects.create()
    newsletter.letter_authored_by.add(request.user)
    newsletter.save()
    return HttpResponseRedirect("view_newsletter/" + str(newsletter.uuid))


@login_required
@staff_member_required
def list_newsletter(request):
    context = {"table": NewsletterTable(Newsletter.objects.all().order_by("-registration_date"))}
    return render(request, "newsletter_list.html", context)


@login_required
@staff_member_required
def did_see_newsletter(request, uuid, token):
    nl = Newsletter.objects.get(uuid=uuid)
    try:
        approval = LetterApprovedBy.objects.get(newsletter=nl, user=request.user)
        if approval.approval_code == int(token):
            approval.did_see_email = True
            approval.save()
            messages.add_message(request, messages.INFO, _("Dein Approval ist nun gültig."))
        else:
            return HttpResponse("Wrong code")
    except Exception:
        return HttpResponse("Not registered")
    return HttpResponseRedirect("/accounts/view_newsletter/" + str(uuid))
"""