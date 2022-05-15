import logging
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator  
from django.template.loader import render_to_string  
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone



logger = logging.getLogger("django")


def send_confirmation_email(user, domain, subject_template="registration/confirmation_email_subject.txt", template="registration/confirmation_email.html", protocol="https"):
    subject = render_to_string(subject_template)
    message = render_to_string(template, {  
        'user': user,  
        'protocol' : protocol,
        'domain': domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
        'token':default_token_generator.make_token(user),  
    })  
    to_email = user.email
    send_mail(subject, message, settings.NOREPLY_MAIL, [to_email])
    user.lastConfirmationMailSent = timezone.now()
    user.save()