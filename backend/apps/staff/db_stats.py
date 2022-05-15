import datetime
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.iamorganisation.models import Organisation
from apps.iofferhelp.models import Helper
from apps.ineedhelp.models import Refugee
from apps.offers.models import GenericOffer

from .models import Newsletter


class RegisterList(list):
    def register_named(self, name, method):
        self.append((name, method))
        return method

    def register(self, name):
        return lambda func: self.register_named(name, func)


class DataBaseStats:
    stat_count = RegisterList()
    stat_list = RegisterList()
    dated_count = RegisterList()

    # TODO: last X days? # noqa: T003

    def __init__(self, length_history_days=7):
        self.length_history_days = length_history_days

    def day_interval(self, i):
        return datetime.date.today() - datetime.timedelta(days=i)

    def day_range(self):
        return range(self.length_history_days, 0 - 2, -1)

    def generate_cum_graph(self, count_func):
        return (
            [self.day_interval(i) for i in self.day_range()],
            [count_func(self, date=self.day_interval(i)) for i in self.day_range()],
        )

    @stat_count.register(name=_("Aktive Staffmember"))
    def admin_count(self, date=None):
        qs = User.objects.all()
        if date is not None:
            qs = qs.filter(date_joined__lte=str(date))
        return qs.filter(is_staff=True).count()

    @stat_count.register(name=_("Akzeptierte Organisationen"))
    def approved_organisation_count(self, date=None):
        qs = Organisation.objects.all()
        if date is not None:
            qs = qs.filter(approvalDate__lte=str(date))
        return qs.filter(isApproved=True, user__validatedEmail=True).count()

    @stat_count.register(name=_("Registrierte Helfende"))
    def validated_helper_count(self, date=None):
        qs = Helper.objects.all()
        if date is not None:
            qs = qs.filter(user__date_joined__lte=str(date))
        return qs.filter(user__validatedEmail=True).count()

    @stat_count.register(name=_("Registrierte Flüchtende"))
    def validated_refugee_count(self, date=None):
        qs = Refugee.objects.all()
        if date is not None:
            qs = qs.filter(user__date_joined__lte=str(date))
        return qs.filter(user__validatedEmail=True).count()

    """@stat_count.register(name=_("Anzahl deaktivierter Helfenden"))
    def deactivated_accounts(self, date=None):
        # no dates are available for this
        return Helper.objects.filter(is_activated=False).count()"""
    

    @stat_count.register(name=_("Anzahl Offers"))
    def active_offers(self, date=None):
        if date is not None:
            return GenericOffer.objects.filter(active=True, incomplete=False, created_at__lte=str(date)).count()
        return GenericOffer.objects.filter(active=True, incomplete=False).count()

    # TODO Contact stats

    @stat_count.register(name=_("Anzahl gesendeter Newsletter"))
    def newsletter_count(self, date=None):
        qs = Newsletter.objects.all()
        if date is not None:
            qs = qs.filter(send_date__lte=str(date))

        return qs.filter(was_sent=True).count()

    def all_stats(self):
        results = [(description, count_func(self)) for description, count_func in self.stat_count]
        for name, m in self.stat_list:
            results.extend(m(self))
        return results

    def all_graphs(self):
        return [(name, self.generate_cum_graph(count_func)) for name, count_func in self.stat_count]
