from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

"""urlpatterns = [
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="registration/logout.html"),
        name="logout",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done_.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_change",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form_.html"
        ),
        name="password_change_form",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete_.html"
        ),
        name="password_reset_complete_",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm_.html",
            post_reset_login=True,
            success_url="/accounts/validate_email",
        ),
        name="password_reset_confirm_",
    ),"""
urlpatterns = [ 
    path(
        "resend_validation_email/<email>",
        views.resend_validation_email,
        name="resend_validation_email",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form_.html", from_email=settings.NOREPLY_MAIL
        ),
        name="password_reset_form",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done_.html"
        ),
        name="password_reset_done",
    ),
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("helper_login", views.helper_login, name="helper_login"),
    path("organisation_login", views.organisation_login, name="organisation_login"),
    path("refugee_login", views.refugee_login, name="refugee_login"),
    path("", include("django.contrib.auth.urls")),
    path("validate_email", views.validate_email, name="validate_email"),
    path("change_email", views.change_email, name="change_email"),
    path("change_email_done", views.change_email_done, name="change_email_done"),
    path("change_email_complete", views.change_email_complete, name="change_email_complete"),
    path("login_redirect", views.login_redirect, name="login_redirect"),
    path("signup_refugee", views.signup_refugee, name="signup_refugee"),
    path("signup_helper", views.signup_helper, name="signup_helper"),
    path("signup_organisation", views.signup_organisation, name="signup_organisation"),
    path("signup_complete", views.signup_complete, name="signup_complete"),
    path("preferences", views.preferences, name="preferences"),
    path("deleted_user", views.delete_me, name="deleted_user"),
    path("change_activation", views.change_activation_ask, name="activate_helper_ask"),
    path("change_activation_confirm", views.change_activation, name="activate_helper"),
    path("i18n/", include("django.conf.urls.i18n")),
]
