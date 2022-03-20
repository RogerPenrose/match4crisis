from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
import numpy as np

from apps.accounts.models import User
from apps.iofferhelp.models import Helper
from apps.iamorganisation.models import Organisation
from apps.ineedhelp.models import Refugee

FAKE_MAIL = "@example.com"


def new_mail(x):
    return ("%s" % x) + FAKE_MAIL


class Command(BaseCommand):
    # has to be "help" because we inherit from django manage.py Command, thus ignore A003
    help = "Populates the database with fake users or deletes them."  # noqa: A003

    def add_arguments(self, parser):

        parser.add_argument(
            "--delete",
            action="store_true",
            help='Delete all users with an email ending in "%s"' % FAKE_MAIL,
        )

        parser.add_argument(
            "--add-refugees", nargs=1, help="Add [N] new refugees to the poll",
        )

        parser.add_argument(
            "--add-helpers", nargs=1, help="Add [N] new helpers to the poll",
        )

        parser.add_argument(
            "--add-organisations", nargs=1, help="Add [N] new organisations to the poll",
        )

        parser.add_argument(
            "--no-input", action="store_true", help="Answer yes to all questions.",
        )

    def handle(self, *args, **options):
        if (
            not options["delete"]
            and options["add_refugees"] is None
            and options["add_organisations"] is None
            and options["add_helpers"] is None
        ):
            self.print_help("", "")
            return None

        self.all_yes = options["no_input"]

        if options["delete"]:
            self.delete_all_fakes()
        if options["add_organisations"] is not None:
            self.add_fake_organisations(int(options["add_organisations"][0]))
        if options["add_helpers"] is not None:
            self.add_fake_helpers(int(options["add_helpers"][0]))
        if options["add_refugees"] is not None:
            self.add_fake_refugees(int(options["add_refugees"][0]))

    def delete_all_fakes(self):
        qs = User.objects.filter(email__contains=FAKE_MAIL)

        n = qs.count()
        if n == 0:
            self.stdout.write(self.style.SUCCESS("No fake users detected."))
            return

        is_sure = (
            input(
                'You are about to delete %s users with emails including "%s". '
                "Are you sure you want to delete them? [y/n]" % (n, FAKE_MAIL)
            )
            if not self.all_yes
            else "y"
        )
        if is_sure != "y":
            self.stdout.write(self.style.WARNING("Users NOT deleted."))
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted these %s fake users." % n))

    def add_fake_helpers(self, n):

        n_users = User.objects.all().count()

        for i in range(n):
            m = new_mail(i + n_users)

            u = User.objects.create(
                username=m,
                email=m,
                isHelper=True,
                validatedEmail=True,
                date_joined=datetime.now() - timedelta(days=np.random.randint(0, 30)),
            )
            u.set_password(m)
            u.save()
            Helper.objects.create(
                user=u,
            )

        self.stdout.write(self.style.SUCCESS("Created %s helpers." % n))

    def add_fake_organisations(self, n):
        n_users = User.objects.all().count()
        for i in range(n):
            m = new_mail(i + n_users)
            u = User.objects.create(
                username=m,
                email=m,
                isOrganisation=True,
                validatedEmail=True,
                date_joined=datetime.now() - timedelta(days=np.random.randint(0, 30)),
            )
            u.set_password(m)
            u.save()
            Organisation.objects.create(
                user=u,
                contactPerson="Jon Skeet",
                isApproved=np.random.choice([True, False], p=[0.7, 0.3]),
                appearsInMap=np.random.choice([True, False], p=[0.8, 0.2]),
            )

        self.stdout.write(self.style.SUCCESS("Created %s organisations." % n))


    def add_fake_refugees(self, n):
        n_users = User.objects.all().count()
        for i in range(n):
            m = new_mail(i + n_users)
            u = User.objects.create(
                username=m,
                email=m,
                isRefugee=True,
                validatedEmail=True,
                date_joined=datetime.now() - timedelta(days=np.random.randint(0, 30)),
            )
            u.set_password(m)
            u.save()
            Refugee.objects.create(
                user=u,
            )

        self.stdout.write(self.style.SUCCESS("Created %s refugees." % n))
