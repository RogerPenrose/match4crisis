"""
Add testing data to database.

route /accounts/add_data aufrufen um user zu generieren
muss in urls.py auskommentiert werden
"""

from django.conf import settings
from django.http import HttpResponse
import numpy as np

from apps.accounts.models import User
from apps.ineedhelp.models import Refugee
from apps.iofferhelp.models import Helper
from apps.iamorganisation.models import Organisation

mail = lambda x: "%s@email.com" % x  # noqa: E731

def delete_fakes():
    User.objects.filter(email__contains="@email.com").delete()


def populate_db(request):
    if settings.DEBUG:
        delete_fakes()
        numRefugees = 2000
        numHelpers = 2000
        numOrganisations = 200

        for i in range(numRefugees):
            m = mail(i)
            pwd = User.objects.make_random_password()
            u = User.objects.create(email=m, password=pwd)
            _ = Refugee.objects.create(
                user=u
            )

        for i in range(numHelpers):
            m = mail(i + numRefugees)

            pwd = User.objects.make_random_password()
            u = User.objects.create(email=m, password=pwd)
            _ = Helper.objects.create(
                user=u,
            )

        for i in range(numOrganisations):
            m = mail(i + numRefugees + numHelpers)
            pwd = User.objects.make_random_password()
            u = User.objects.create(email=m, password=pwd)
            _ = Organisation.objects.create(
                user=u, organisationName=f"Organisation {i}", contactPerson="XY"
            )

        
        return HttpResponse("Done. %s entries." % User.objects.all().count())
    return HttpResponse("Access forbidden: Not in debug mode.")
