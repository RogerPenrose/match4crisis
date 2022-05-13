import logging
from django.conf import settings
from django.core.mail import send_mass_mail, EmailMessage
from django.template.loader import render_to_string  

logger = logging.getLogger("django")

def send_help_request_emails(organisation, helpRequest, recipients, domain, subject_template="help_request_email_subject.txt", template="help_request_email.html", protocol="https"):
    # TODO split up emails if recipients is too large?
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

def send_email_to_organisation(helper, helpRequest, message, domain, subject_template="contact_organisation_email_subject.txt", template="contact_organisation_email.html", protocol="https"):
    subject = render_to_string(subject_template)
    content = render_to_string(template, {  
        'organisation': helpRequest.organisation,  
        'sender': helper.user,  
        'helpRequest' : helpRequest,
        'message' : message,
        'protocol' : protocol,
        'domain': domain,
    })  
    from_email = settings.NOREPLY_MAIL
    to_email = helpRequest.organisation.user.email
    reply_to_email = helper.user.email

    email = EmailMessage(subject, content, from_email, [to_email], reply_to=[reply_to_email])
    email.send()