from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path

from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm

from . import views

urlpatterns = [ 
    path(
        "resend_confirmation_email",
        views.resend_confirmation_email,
        name="resend_confirmation_email",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_management/password_reset_form.html", 
            from_email=settings.NOREPLY_MAIL, 
            form_class=CustomPasswordResetForm, 
            email_template_name = "password_management/password_reset_email.html", 
            subject_template_name = "password_management/password_reset_email_subject.txt"
        ),
        name="password_reset_form",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_management/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            post_reset_login=True,
            success_url="/accounts/reset/done",
        ),
        name="password_reset_confirm_",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_management/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_management/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="password_management/password_change_form.html",
            form_class=CustomPasswordChangeForm,
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password_management/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("thanks", views.thanks, name="thanks"),
    path("helper_login", views.helper_login, name="helper_login"),
    path("organisation_login", views.organisation_login, name="organisation_login"),
    path("refugee_login", views.refugee_login, name="refugee_login"),
    path("confirm_email/<uidb64>/<token>/", views.confirm_email, name="confirm_email"),
    path("change_email", views.change_email, name="change_email"),
    path("change_email_done", views.change_email_done, name="change_email_done"),
    path("confirm_change_email/<uidb64>/<token>/", views.confirm_change_email, name="confirm_change_email"),
    path("login_redirect", views.login_redirect, name="login_redirect"),
    path("signup_refugee", views.signup_refugee, name="signup_refugee"),
    path("signup_helper", views.signup_helper, name="signup_helper"),
    path("signup_organisation", views.signup_organisation, name="signup_organisation"),
    path("signup_complete", views.signup_complete, name="signup_complete"),
    path("preferences", views.preferences, name="preferences"),
    path("delete_me", views.delete_me, name="delete_me"),
    path("deleted_user", views.deleted_user, name="deleted_user"),
    path("i18n/", include("django.conf.urls.i18n")),
]
