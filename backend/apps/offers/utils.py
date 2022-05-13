import logging

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string  

logger = logging.getLogger("django")


def send_email_to_helper(offer, message, recipient, sender, domain, subject_template="offers/contact_helper_email_subject.txt", template="offers/contact_helper_email.html", protocol="https"):
    subject = render_to_string(subject_template)
    content = render_to_string(template, {  
        'recipient': recipient,  
        'sender': sender,  
        'offer' : offer,
        'message' : message,
        'protocol' : protocol,
        'domain': domain,
    })  
    to_email = recipient.email

    email = EmailMessage(subject, content, settings.NOREPLY_MAIL, [to_email], reply_to=[sender.email])
    email.send()