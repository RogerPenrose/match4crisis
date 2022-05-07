import logging
from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string  

logger = logging.getLogger("django")

def send_help_request_emails(organisation, helpRequest, recipients, domain, subject_template="help_request_email_subject.txt", template="help_request_email.html", protocol="https"):
    if recipients.count() > 950:
        # TODO split up emails
        pass


    else:
        subject = render_to_string(subject_template)
        from_email = settings.NOREPLY_MAIL
        emails = []
        for recip in recipients:
            message = render_to_string(template, {  
                'organisation': organisation,
                'recipient' : recip,
                'helpRequest' : helpRequest,
                'protocol' : protocol,
                'domain': domain,
            })  
            emails.append((subject, message, from_email, [recip.email]))

        send_mass_mail(emails)