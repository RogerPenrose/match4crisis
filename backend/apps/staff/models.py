import logging
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import gettext_lazy as _
import numpy as np

from apps.accounts.models import User

from .email_utils import send_mass_mail_sendgrid

logger = logging.getLogger("django")

class NewsletterState:
    BEING_EDITED = 1
    UNDER_APPROVAL = 2
    READY_TO_SEND = 3
    SENT = 4

ONLY_VALIDATED = 0
ONLY_NOT_VALIDATED = 1
ALL = 2
VALIDATED_AND_APPROVED = 3

VALIDATION_CHOICES = (
    (ONLY_VALIDATED, _("validierte")),
    (ONLY_NOT_VALIDATED, _("nicht validierte")),
    (ALL, _("validierte und nicht validierte")),
    (VALIDATED_AND_APPROVED, _("validiert und von uns approved")),
)


class Newsletter(models.Model):
    #uuid = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

    registration_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    last_edited_date = models.DateTimeField(default=None, blank=True, null=True)
    frozen_date = models.DateTimeField(default=None, blank=True, null=True)
    send_date = models.DateTimeField(default=None, blank=True, null=True)

    letter_authored_by = models.ManyToManyField(to=User, related_name="authored_letters")
    letter_approved_by = models.ManyToManyField(
        to=User, related_name="approved_letters", through="LetterApprovedBy"
    )
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_newsletters")
    frozen_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="frozen_newsletters"
    )

    subject = models.CharField(max_length=200, default="")
    message = models.TextField(default="", max_length=1000000)

    was_sent = models.BooleanField(default=False)

    send_to_organisations = models.BooleanField(default=False)
    send_to_helpers = models.BooleanField(default=False)
    send_to_refugees = models.BooleanField(default=False)

    user_validation_required = models.IntegerField(
        choices=VALIDATION_CHOICES, default=ONLY_VALIDATED, blank=False
    )

    def __str__(self) -> str:
        return 'Newsletter: %s' % self.subject

    def sending_state(self):
        if self.was_sent:
            return NewsletterState.SENT
        else:
            if self.frozen_by is None:
                return NewsletterState.BEING_EDITED
            elif self.required_approvals() > 0:
                return NewsletterState.UNDER_APPROVAL
            else:
                return NewsletterState.READY_TO_SEND

    def unfreeze(self):
        self.frozen_by = None
        self.frozen_date = None
        LetterApprovedBy.objects.filter(newsletter=self).delete()

    def approve_from(self, user):
        self.letter_approved_by.add(user)

    def send(self, user):
        self.send_newsletter_out()
        self.send_date = timezone.now()
        self.was_sent = True
        self.sent_by = user

    def freeze(self, user):
        self.frozen_by = user
        self.frozen_date = timezone.now()

    def edit_meta_data(self, user):
        self.letter_authored_by.add(user)
        self.last_edited_date = timezone.now()

    def send_testmail_to(self, email_receipient):
        email = EmailMessage(
            subject=self._subject(),
            body=self.message,
            from_email=settings.NOREPLY_MAIL,
            to=[email_receipient],
        )
        email.content_subtype = "html"
        email.send()

    def has_been_approved_by(self, user):
        return (
            LetterApprovedBy.objects.filter(newsletter=self, user=user, did_see_email=True).count()
            == 1
        )

    def required_approvals(self):
        return (
            settings.NEWSLETTER_REQUIRED_APPROVERS
            - LetterApprovedBy.objects.filter(newsletter=self, did_see_email=True).count()
        )

    def send_approval_mail(self, approval, host):
        body = "<h3>Link zum Approven ganz unten</h3><hr>"
        body += self.message
        body += (
            '<hr><a href="https://%s/staff/view_newsletter/%s"> Ich habe Probleme gefunden und will den '
            "Newsletter bearbeiten.</a><br>" % (host, self.id)
        )
        body += (
            '<a href="https://%s">Ich bestätige, dass diese E-Mail als Newsletter'
            " abgeschickt werden darf.</a>" % approval.verify_url(host)
        )
        email = EmailMessage(
            subject=self._subject(),
            body=body,
            from_email=settings.NOREPLY_MAIL,
            to=[approval.user.email],
        )
        email.content_subtype = "html"
        email.send()

    def _subject(self):
        return "[match4crisis] " + str(self.subject)

    def send_newsletter_out(self):
        if self.sending_state() != NewsletterState.READY_TO_SEND:
            raise ValueError(
                "The newsletter is not ready to send, so you cannot send out an email."
            )

        organisation_filter = {"isOrganisation": True}
        helper_filter = {"isHelper": True}
        refugee_filter = {"isRefugee": True}

        if self.user_validation_required == ONLY_VALIDATED:
            organisation_filter["validatedEmail"] = True
            helper_filter["validatedEmail"] = True
            refugee_filter["validatedEmail"] = True
        elif self.user_validation_required == VALIDATED_AND_APPROVED:
            organisation_filter["validatedEmail"] = True
            organisation_filter["organisation__isApproved"] = True
            helper_filter["validatedEmail"] = True
            refugee_filter["validatedEmail"] = True
        elif self.user_validation_required == ONLY_NOT_VALIDATED:
            organisation_filter["validatedEmail"] = False
            helper_filter["validatedEmail"] = False
            refugee_filter["validatedEmail"] = False
        elif ALL:
            pass

        if self.send_to_organisations:
            recipient_organisations_qs = User.objects.filter(**organisation_filter).values_list(
                "email", flat=True
            )
            n_organisation = recipient_organisations_qs.count()
            logger.info("Starting to send out newsletter to %s organisations...", n_organisation)
            self._send_mail(recipient_organisations_qs, n_organisation)

        if self.send_to_helpers:
            recipient_helper_qs = User.objects.filter(**helper_filter).values_list(
                "email", flat=True
            )
            n_helpers = recipient_helper_qs.count()
            logger.info("Starting to send out newsletter to %s helpers...", n_helpers)
            self._send_mail(recipient_helper_qs, n_helpers)

        if self.send_to_refugees:
            recipient_refugee_qs = User.objects.filter(**refugee_filter).values_list(
                "email", flat=True
            )
            n_refugees = recipient_refugee_qs.count()
            logger.info("Starting to send out newsletter to %s refugees...", n_refugees)
            self._send_mail(recipient_refugee_qs, n_refugees)

    def _send_mail(self, recipients, n):

        chunksize = 950
        # max allowed by sendgrid: 1k (but they have weird extra limitations, so be sure)
        # https://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/index.html#-Limitations

        for i in range((n // chunksize) + 1):
            pos = i * chunksize
            send_mass_mail_sendgrid(
                recipient_list=recipients[pos : min(pos + chunksize, n)],
                subject=self._subject(),
                html_body=self.message,
                from_mail=settings.NOREPLY_MAIL,
            )

def random_number():
    return np.random.randint(0, 100000)

class LetterApprovedBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    approval_code = models.IntegerField(default=random_number)
    did_see_email = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "user",
            "newsletter",
        )

    def verify_url(self, host):
        return "%s/staff/did_see_newsletter/%s/%s" % (
            host,
            self.newsletter.id,
            self.approval_code,
        )
