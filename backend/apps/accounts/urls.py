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
    path("", include("django.contrib.auth.urls")),
    path("validate_email", views.validate_email, name="validate_email"),
    path("change_email", views.change_email, name="change_email"),
    path("change_email_done", views.change_email_done, name="change_email_done"),
    path("change_email_complete", views.change_email_complete, name="change_email_complete"),
    path("login_redirect", views.login_redirect, name="login_redirect"),
    path("signup_refugee", views.signup_refugee, name="signup_refugee"),
    path("signup_helper", views.signup_helper, name="signup_helper"),
    path("signup_organisation", views.signup_organisation, name="signup_organisation"),
    path("preferences", views.preferences, name="preferences"),
    path("deleted_user", views.delete_me, name="deleted_user"),
    #path("profile_helper", views.edit_helper_profile, name="edit_helper_profile"),
    #path("profile_organisation", views.edit_organisation_profile, name="edit_organisation_profile"),
    #path("approve_organisations", views.approve_organisations, name="approve_organisations"),
    # path(
    #     "change_organisation_approval/<str:uuid>/",
    #     views.change_organisation_approval,
    #     name="change_organisation_approval",
    # ),
    path("delete_organisation/<str:uuid>/", views.delete_organisation, name="delete_organisationl"),
    #path("count", views.UserCountView.as_view(), name="count"),
    path("change_activation", views.change_activation_ask, name="activate_helper_ask"),
    path("change_activation_confirm", views.change_activation, name="activate_helper"),
    #path("view_newsletter/<uuid>", views.view_newsletter, name="view_newsletter"),
    #path("new_newsletter", views.new_newsletter, name="new_newsletter"),
    #path("list_newsletter", views.list_newsletter, name="list_newsletter"),
    #path("did_see_newsletter/<uuid>/<token>", views.did_see_newsletter, name="did_see_newsletter"),
    path("profile_staff", views.staff_profile, name="staff_profile"),
    path("i18n/", include("django.conf.urls.i18n")),
]
