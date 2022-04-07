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
        "login/",
        views.CustomLoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("", include("django.contrib.auth.urls")),
    path("validate_email", views.validate_email, name="validate_email"),
    path("login_redirect", views.login_redirect, name="login_redirect"),
    path("delete_me_ask", views.delete_me_ask, name="delete_me_ask"),
    path("delete_me", views.delete_me, name="delete_me"),
    path("signup_refugee", views.signup_refugee, name="signup_refugee"),
    path("signup_helper", views.signup_helper, name="signup_helper"),
    path("signup_organisation", views.signup_organisation, name="signup_organisation"),
    path("preferences", views.preferences, name="preferences"),
    #path("count", views.UserCountView.as_view(), name="count"),
    path("change_activation", views.change_activation_ask, name="activate_helper_ask"),
    path("change_activation_confirm", views.change_activation, name="activate_helper"),
    path("i18n/", include("django.conf.urls.i18n")),
]
