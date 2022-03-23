from django.contrib import auth
from django.test import Client, TestCase
import numpy as np

from apps.accounts.models import User
from apps.iofferhelp.models import AUSBILDUNGS_TYPEN_COLUMNS, Helper
from apps.iamorganisation.models import Organisation


def generate_random_helper(countrycode="DE", plz="14482", i=0, validated_email=False):
    m = str(i) + "helper@email.de"
    pwd = User.objects.make_random_password()
    kwd = dict(
        zip(
            AUSBILDUNGS_TYPEN_COLUMNS,
            np.random.choice([True, False], size=len(AUSBILDUNGS_TYPEN_COLUMNS)),
        )
    )

    u = User.objects.create(email=m, isHelper=True, validated_email=validated_email)
    u.set_password(pwd)
    s = Helper.objects.create(
        user=u,
        countrycode=countrycode,
        plz=plz,
        availability_start="{}-{:02d}-{:02d}".format(2020, 3, 23),
        **kwd
    )
    u.save()
    s.save()
    return m, pwd, s.uuid


def generate_random_organisation(
    countrycode="DE", plz="14482", i=0, validated_email=False,
):
    m = str(i) + "organisation@email.de"
    pwd = User.objects.make_random_password()
    u = User.objects.create(email=m, isOrganisation=True, validated_email=validated_email)
    u.set_password(pwd)
    s = Organisation.objects.create(
        user=u, countrycode=countrycode, plz=plz, ansprechpartner="XY", sonstige_infos="yeaah",
    )
    u.save()
    s.save()
    return m, pwd, s.uuid


def generate_staff_user(i=0):
    m = str(i) + "staff@email.de"
    pwd = User.objects.make_random_password()
    u = User.objects.create_superuser(email=m)
    u.set_password(pwd)
    u.save()
    return m, pwd


class UrlEndpointTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT="Mozilla/5.0")

    def test_http_get_endpoints(self):
        assert self.client.get("/", {}).status_code == 200
        assert self.client.get("/about/", {}).status_code == 200
        assert self.client.get("/impressum/", {}).status_code == 200
        assert self.client.get("/dataprotection/", {}).status_code == 200
        assert self.client.get("/legal-questions/", {}).status_code == 200

        # Mapview
        assert self.client.get("/mapview/", {}).status_code == 200

        # Accounts
        assert self.client.get("/accounts/signup_helper", {}).status_code == 200
        assert self.client.get("/accounts/signup_organisation", {}).status_code == 200
        assert self.client.get("/accounts/password_reset/", {}).status_code == 200
        assert self.client.get("/accounts/login/", {}).status_code == 200

    def test_count_url(self):
        generate_random_helper(validated_email=True)
        response = self.client.get("/accounts/count", {})
        assert response.status_code == 200
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"facility_count": 0, "user_count": 1},
        )

        generate_random_organisation(validated_email=True)
        response = self.client.get("/accounts/count", {})
        assert response.status_code == 200
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"facility_count": 1, "user_count": 1},
        )

    def test_helper(self):
        helper_email, helper_password, _ = generate_random_helper()
        assert self.client.post("/accounts/logout/", {}).status_code == 200

        response = self.client.post(
            "/accounts/password_reset", {"email": helper_email}, follow=True
        )
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_reset/done # noqa: T003

        response = self.client.post(
            "/accounts/validate_email", {"email": helper_email}, follow=True
        )
        assert "/accounts/login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        response = self.client.post(
            "/accounts/login/",
            {"email": helper_email, "password": helper_password,},
            follow=True,
        )
        assert auth.get_user(self.client).email == helper_email

        assert Helper.objects.get(user__email=helper_email).user.validated_email is False
        response = self.client.post(
            "/accounts/validate_email", {"email": helper_email}, follow=True
        )
        assert response.status_code == 200
        assert Helper.objects.get(user__email=helper_email).user.validated_email

        response = self.client.post(
            "/accounts/password_change",
            {
                "email": helper_email,
                "new_password1": helper_password,
                "new_password2": helper_password,
            },
            follow=True,
        )
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_change/done # noqa: T003

        assert self.client.get("/mapview/", {}).status_code == 200

        response = self.client.get("/accounts/profile_redirect", follow=True)
        assert "profile_helper" in response.redirect_chain[0][0]
        assert self.client.get("/accounts/profile_helper", {}).status_code == 200

        assert self.client.get("/accounts/logout/", {}).status_code == 200
        assert auth.get_user(self.client).is_anonymous

        response = self.client.post(
            "/accounts/login/",
            {"email": helper_email, "password": helper_password,},
            follow=True,
        )
        assert auth.get_user(self.client).email == helper_email

        # Test view list of studens without being logged in as helper. Should redirect!
        response = self.client.get("/iamorganisation/helpers/DE/14482/0", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        # Test admin view when logged in as helper. Should redirect
        response = self.client.get("/accounts/approve_organisations", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        m1, p1, uuid1 = generate_random_organisation("DE", "14482", 1337)
        m2, p2, uuid2 = generate_random_organisation("DE", "10115", 1234)
        m3, p3, uuid3 = generate_random_organisation("AT", "4020", 420)
        response = self.client.get("/iamorganisation/organisation_view/" + str(uuid1) + "/")
        assert response.status_code == 200

        response = self.client.get("/iamorganisation/organisations/DE/14482")
        assert response.status_code == 200

        assert self.client.get("/accounts/delete_me_ask", {}).status_code == 200
        assert self.client.get("/accounts/delete_me", {}).status_code == 200

        response = self.client.post(
            "/accounts/login/",
            {"email": helper_email, "password": helper_password,},
            follow=True,
        )
        assert auth.get_user(self.client).is_anonymous

        # Only available to logged in users, should redirect
        response = self.client.get("/iamorganisation/organisation_view/" + str(uuid1) + "/", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        # Only available to logged in users, should redirect
        response = self.client.get("/iamorganisation/organisations/DE/14482", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

    def test_organisation(self):
        organisation_email, organisation_password, uuid = generate_random_organisation()

        assert self.client.post("/accounts/logout/", {}).status_code == 200

        response = self.client.post(
            "/accounts/password_reset", {"email": organisation_email}, follow=True
        )
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_reset/done # noqa: T003

        response = self.client.post(
            "/accounts/validate_email", {"email": organisation_email}, follow=True
        )
        assert "/accounts/login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        response = self.client.post(
            "/accounts/login/",
            {"email": organisation_email, "password": organisation_password,},
            follow=True,
        )
        assert auth.get_user(self.client).email == organisation_email

        assert Organisation.objects.get(user__email=organisation_email).user.validated_email is False
        response = self.client.post(
            "/accounts/validate_email", {"email": organisation_email}, follow=True
        )
        assert response.status_code == 200
        assert Organisation.objects.get(user__email=organisation_email).user.validated_email

        response = self.client.post(
            "/accounts/password_change",
            {
                "email": organisation_email,
                "new_password1": organisation_password,
                "new_password2": organisation_password,
            },
            follow=True,
        )
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_change/done  # noqa: T003

        assert self.client.get("/mapview/", {}).status_code == 200
        # TODO: Test Detailansicht for a organisation!  # noqa: T003

        response = self.client.get("/accounts/profile_redirect", follow=True)
        assert response.status_code == 200
        assert "profile_organisation" in response.redirect_chain[0][0]
        assert self.client.get("/accounts/profile_organisation", {}).status_code == 200

        assert self.client.get("/accounts/logout/", {}).status_code == 200
        assert auth.get_user(self.client).is_anonymous

        response = self.client.post(
            "/accounts/login/",
            {"email": organisation_email, "password": organisation_password,},
            follow=True,
        )
        assert auth.get_user(self.client).email == organisation_email

        # Test view list of helpers with being logged in as organisation. Should work!
        response = self.client.get("/iamorganisation/helpers/DE/14482/0", follow=True)
        assert response.status_code == 200
        assert len(response.redirect_chain) == 0

        # Test admin view when logged in as organisation. Should redirect
        response = self.client.get("/accounts/approve_organisations", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        response = self.client.get("/iamorganisation/organisation_view/" + str(uuid) + "/")
        assert response.status_code == 200

        response = self.client.get("/iamorganisation/organisations/DE/14482")
        assert response.status_code == 200

        m1, p1, uuid1 = generate_random_helper("DE", "14482", 1337, validated_email=True)
        m2, p2, uuid2 = generate_random_helper("DE", "10115", 1234, validated_email=True)
        m3, p3, uuid3 = generate_random_helper("DE", "10115", 12345, validated_email=False)
        m4, p4, uuid4 = generate_random_helper("AT", "4020", 420, validated_email=True)
        response = self.client.get("/iamorganisation/helpers/DE/14482/0")

        assert "1 Helfer*innen" in str(response.content)
        assert response.status_code == 200

        response = self.client.get("/iamorganisation/helpers/DE/14482/50")
        assert "2 Helfer*innen" in str(response.content)
        assert response.status_code == 200

        assert self.client.get("/accounts/delete_me_ask", {}).status_code == 200
        assert self.client.get("/accounts/delete_me", {}).status_code == 200

        response = self.client.post(
            "/accounts/login/",
            {"email": organisation_email, "password": organisation_password,},
            follow=True,
        )
        assert auth.get_user(self.client).is_anonymous

        # Test view list of studens without being logged in. Should redirect!
        response = self.client.get("/iamorganisation/helpers/DE/14482/0", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        # Test admin view as logged out user. Should redirect
        response = self.client.get("/accounts/approve_organisations", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        organisation_email, organisation_password, uuid = generate_random_organisation(i=9999)
        response = self.client.post(
            "/accounts/login/",
            {"email": organisation_email, "password": organisation_password,},
            follow=True,
        )
        assert auth.get_user(self.client).email == organisation_email
        assert response.status_code == 200
        assert "login_redirect" in response.redirect_chain[0][0]

    def test_sudent_individual_view(self):
        staff_email, staff_password = generate_staff_user()
        organisation_email, organisation_password, organisation_uuid = generate_random_organisation()
        helper_email, helper_password, helper_uuid = generate_random_helper()

        response = self.client.post(
            "/accounts/login/",
            {"email": helper_email, "password": helper_password,},
            follow=True,
        )
        response = self.client.get("/iofferhelp/view_helper/" + str(helper_uuid), follow=True)
        assert response.status_code == 200
        assert "/accounts/profile_helper" in response.redirect_chain[0][0]

        # TOOD: test which emails can be seen here!
        response = self.client.post(
            "/accounts/login/", {"email": staff_email, "password": staff_password,}, follow=True,
        )
        response = self.client.get("/iofferhelp/view_helper/" + str(helper_uuid))
        assert response.status_code == 200

        # TOOD: test which emails can be seen here!
        response = self.client.post(
            "/accounts/login/",
            {"email": organisation_email, "password": organisation_password,},
            follow=True,
        )
        response = self.client.get("/iofferhelp/view_helper/" + str(helper_uuid))
        assert response.status_code == 200

    def test_admin(self):
        staff_email, staff_password = generate_staff_user()

        assert self.client.post("/accounts/logout/", {}).status_code == 200

        response = self.client.post("/accounts/password_reset", {"email": staff_email}, follow=True)
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_reset/done # noqa: T003

        response = self.client.post(
            "/accounts/login/", {"email": staff_email, "password": staff_password,}, follow=True,
        )
        assert auth.get_user(self.client).email == staff_email

        response = self.client.post(
            "/accounts/password_change",
            {
                "email": staff_email,
                "new_password1": staff_password,
                "new_password2": staff_password,
            },
            follow=True,
        )
        # print(response.redirect_chain)
        assert response.status_code == 200
        # TODO: why does this not redirect to /accounts/password_change/done # noqa: T003

        assert self.client.get("/mapview/", {}).status_code == 200
        # TODO: Test Detailansicht for a organisation! # noqa: T003

        response = self.client.get("/accounts/profile_redirect", follow=True)
        assert response.status_code == 200
        assert "profile_staff" in response.redirect_chain[0][0]

        response = self.client.get("/accounts/approve_organisations", follow=True)
        assert response.status_code == 200

        assert self.client.get("/accounts/logout/", {}).status_code == 200
        assert auth.get_user(self.client).is_anonymous

        response = self.client.post(
            "/accounts/login/", {"email": staff_email, "password": staff_password,}, follow=True,
        )
        assert auth.get_user(self.client).email == staff_email

        # Test view list of studens witbeing logged in as staff user
        # Current behavior: Should redirect!
        # TODO: discuss what the behavior of this should be! # noqa: T003
        response = self.client.get("/iamorganisation/helpers/DE/14482/0", follow=True)
        assert "login" in response.redirect_chain[0][0]
        assert response.status_code == 200

        assert self.client.get("/accounts/delete_me_ask", {}).status_code == 200
        assert self.client.get("/accounts/delete_me", {}).status_code == 200

        response = self.client.post(
            "/accounts/login/", {"email": staff_email, "password": staff_password,}, follow=True,
        )
        assert auth.get_user(self.client).is_anonymous

        response = self.client.get("/iamorganisation/helpers/DE/14482/0", follow=True)
