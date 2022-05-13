import logging
from django.conf import settings

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.tokens import default_token_generator  
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.encoding import  force_text
from django.utils.http import urlsafe_base64_decode

from django.views.generic import TemplateView
from apps.iofferhelp.forms import HelperCreationForm, HelperPreferencesForm
from apps.ineedhelp.forms import RefugeeCreationForm, RefugeePreferencesForm
from rest_framework.views import APIView

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
from apps.offers.models import SPECIAL_CASE_OFFERS, GenericOffer, OFFER_MODELS

from .utils import send_confirmation_email, send_password_set_email
from .decorator import organisationRequired, helperRequired
from .models import User
from .forms import ChangeEmailForm, CommonPreferencesForm, CustomAuthenticationForm, CustomPasswordResetForm, ResendConfirmationEmailForm

logger = logging.getLogger(__name__)


def signup_refugee(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = RefugeeCreationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            user, refugee = form.save()
            send_confirmation_email(user, get_current_site(request).domain)
            return redirect('thanks')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RefugeeCreationForm()

    return render(request, "signup_refugee.html", {"form": form})



def signup_helper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = HelperCreationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            user, helper = form.save()
            # If the user got here through the /iofferhelp/choose_help page, get the chosen help data from the request session
            if('chosenHelp' in request.session):
                chosenHelp = request.session['chosenHelp'].items()
                chosenHelpSubchoices = request.session['chosenHelpSubchoices']
                for offerType, chosen in chosenHelp:    

                    if chosen:
                        # Create a new incomplete offer of this type; 
                        # if subchoices are active for this offer type; create one offer for every chosen subchoice
                        if offerType in chosenHelpSubchoices:
                            for subchoice in chosenHelpSubchoices[offerType]:
                                logger.info(offerType + " " + subchoice)
                                genericOffer = GenericOffer(offerType=offerType, userId=user, active=False, incomplete=True)
                                genericOffer.save()
                                specOffer = OFFER_MODELS[offerType](genericOffer=genericOffer, helpType=subchoice)
                                specOffer.save()
                        else:
                            genericOffer = GenericOffer(offerType=offerType, userId=user, active=False, incomplete=True)
                            genericOffer.save()
                            specOffer = OFFER_MODELS[offerType](genericOffer=genericOffer)
                            specOffer.save()
                    
            send_confirmation_email(user, get_current_site(request).domain)
            
            return redirect('thanks')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HelperCreationForm()

    return render(request, "signup_helper.html", {"form": form})



def signup_organisation(request):
    if request.method == "POST":
        form_info = OrganisationFormInfoSignUp(request.POST)

        if form_info.is_valid():
            user, organisation = register_organisation_in_db(request, form_info.cleaned_data)
            send_confirmation_email(user, get_current_site(request).domain)
            return redirect('thanks')
    else:
        form_info = OrganisationFormInfoSignUp()
        # form_user = OrganisationSignUpForm()
    form_info.helper.form_tag = False
    return render(request, "signup_organisation.html", {"form_info": form_info})

def thanks(request):
    return render(request, "thanks.html")

def signup_complete(request):
    return render(request, "signup_complete.html")

@transaction.atomic
def register_organisation_in_db(request, formData):

    pwd = formData["password1"]
    user = User.objects.create(email=formData["email"], isOrganisation=True)
    user.set_password(pwd)
    user.phoneNumber = formData["phoneNumber"]
    # In Prod: user should be unable to log in until email is confirmed
    # Bypass email confirmation in Dev (where settings.DEBUG is True)
    user.validatedEmail = settings.DEBUG
    user.save()

    organisation = Organisation.objects.create(user=user)
    organisation = OrganisationFormInfoCreate(request.POST, instance=organisation)
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
        return HttpResponseRedirect("/staff/staff_dashboard")

    else:
        # TODO: throw 404  # noqa: T003
        logger.warning(
            "User is unknown type, login redirect not possible", extra={"request": request},
        )
        return HttpResponse("Something wrong in database")

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

@login_required
def delete_me(request):
    user = request.user
    logout(request)
    logger.info("Delete User with email %s", user.email, extra={"request": request})
    user.delete()
    return redirect("deleted_user")

def deleted_user(request):
    return render(request, 'deleted_user.html')


def confirm_email(request, uidb64, token):
    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and user.validatedEmail:
        return render(request, "email_already_confirmed.html")
    elif user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.validatedEmail = True
        user.emailValidationDate = timezone.now()
        user.lastConfirmationMailSent = None
        user.save()
        return render(request, "signup_complete.html")
    else:
        return render(request, "confirmation_link_invalid.html")

@login_required
def change_email(request):
    if request.method == "POST":
        logger.info("E-Mail change request", extra={"request": request})
        form = ChangeEmailForm(request.POST)

        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data["email"]
            user.validatedEmail = False
            user.emailValidationDate = None
            user.save()
            logout(request)
            send_confirmation_email(
                user, 
                get_current_site(request).domain, 
                subject_template="registration/change_email_address_email_subject.txt",
                template="registration/change_email_address_email.html"
                )
            return redirect("change_email_done")
    else:
        form = ChangeEmailForm()

    return render(request, "change_email.html", {"form":form})

def change_email_done(request):
    return render(request, "change_email_done.html")

def confirm_change_email(request, uidb64, token):
    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and user.validatedEmail:
        return render(request, "email_already_confirmed.html")
    elif user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.validatedEmail = True
        user.emailValidationDate = timezone.now()
        user.lastConfirmationMailSent = None
        user.save()
        return render(request, "change_email_complete.html")
    else:
        return render(request, "confirmation_link_invalid.html")    

def resend_confirmation_email(request):
    if request.method == "POST":
        logger.info("Resend confirmation email request", extra={"request": request})
        form = ResendConfirmationEmailForm(request.POST)

        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            send_confirmation_email(user, get_current_site(request).domain)
            return redirect('thanks')
    else:
        form = ResendConfirmationEmailForm()

    return render(request, "resend_confirmation_email.html", {"form":form})


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
        logger.info("Login Attempt (%s)", request.POST["email"])
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        logger.info("Login successful (%s)", form.cleaned_data["email"])
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning("Login failure (%s)", getattr(form.data, "email", ""))
        return super().form_invalid(form)

    def get_usertype_data(self, request, *args, **kwargs):
        context = super(CustomLoginView, self).get_context_data(**kwargs)
        if request.user.is_authenticated:
            if request.user.isHelper:
                context['userType'] = _("Helfer*in")
            elif request.user.isRefugee:
                context['userType'] = _("Hilfesuchende*r")
            elif request.user.isOrganisation:
                context['userType'] = _("Organisation")
            elif request.user.is_superuser:
                context['userType'] = _("Admin")
            elif request.user.is_staff:
                context['userType'] = _("Staff-User")
        if "requiredUserType" in request.session:
            context["requiredUserType"] = request.session["requiredUserType"]
        return context

    def get(self, request, *args, **kwargs) -> HttpResponse:
        return self.render_to_response(self.get_usertype_data(request, *args, **kwargs))

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.render_to_response(self.get_usertype_data(request, form=form))

def helper_login(request):
    request.session["requiredUserType"] = _("Helfer*in")
    resp =  HttpResponseRedirect("login")
    resp["Location"] += "?next="+request.GET['next']
    return resp

def refugee_login(request):
    request.session["requiredUserType"] = _("Hilfesuchende*r")
    resp =  HttpResponseRedirect("login")
    resp["Location"] += "?next="+request.GET['next']
    return resp

def organisation_login(request):
    request.session["requiredUserType"] = _("Organisation")
    resp =  HttpResponseRedirect("login")
    resp["Location"] += "?next="+request.GET['next']
    return resp

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

@method_decorator(login_required, name='dispatch')
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
    elif(user.isHelper):
        userTypeClass = Helper
        userTypeForm = HelperPreferencesForm
    else: 
        return HttpResponse("Unknown user type")

    specificAccount = userTypeClass.objects.get(user=user)
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            comPrefForm = CommonPreferencesForm(request.POST, instance=user)
            specPrefForm = userTypeForm(request.POST, request.FILES, instance = specificAccount)
            if comPrefForm.is_valid() and specPrefForm.is_valid():
                user = comPrefForm.save()
                specificAccount = specPrefForm.save()
                return login_redirect(request)
        else:
            comPrefForm = CommonPreferencesForm(instance=user)
            specPrefForm = userTypeForm(instance = specificAccount)
        return render(request, "preferences.html", {"comPrefForm": comPrefForm, "specPrefForm": specPrefForm})
    else:
        return HttpResponse("User is anonymous or not active")