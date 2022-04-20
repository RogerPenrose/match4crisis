from django.core.management.base import BaseCommand, no_translations
from django.conf import settings
from apps.accounts.models import User

from .createfakeusers import FAKE_MAIL

class Command(BaseCommand):
    help = "Deletes all fake users ending in '%s'" % FAKE_MAIL
    
    
    def handle(self, *args, **options):

        self.stdout.write(str(options))

       
        if settings.DEBUG:
            self.delete_all_fakes()
            return
        return ("Access forbidden: Not in debug mode.")


    
    def delete_all_fakes(self):
        qs = User.objects.filter(email__contains=FAKE_MAIL)

        n = qs.count()
        if n == 0:
            self.stdout.write(self.style.SUCCESS("No fake users detected."))
            return

        is_sure = input(
                'You are about to delete %s users with emails including "%s". '
                "Are you sure you want to delete them? [y/n]" % (n, FAKE_MAIL)
            )

        if is_sure != "y":
            self.stdout.write(self.style.WARNING("Users NOT deleted."))
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted %s fake users." % n))