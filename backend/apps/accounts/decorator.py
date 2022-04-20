from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

def refugeeRequired(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="refugee_login"):
    """
    Redirect unauthenticated refugees to login page.

    Decorator for views that checks that the logged in user is a refugee,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.isRefugee,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def helperRequired(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="helper_login"):
    """
    Redirect unauthenticated helpers to login page.

    Decorator for views that checks that the logged in user is a helper,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.isHelper,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def organisationRequired(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="organisation_login"):
    """
    Redirect unauthenticated organisations to login page.

    Decorator for views that checks that the logged in user is a organisation,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.isOrganisation,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
