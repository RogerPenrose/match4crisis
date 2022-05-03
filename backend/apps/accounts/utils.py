import logging
from random import choice
from string import ascii_lowercase, digits

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator  
from django.template.loader import render_to_string  
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from .models import User

logger = logging.getLogger("django")


def send_password_set_email(
    email, host, subject_template, template="registration/password_set_email_.html"
):
    form = PasswordResetForm({"email": email})
    logger.debug("Sending Password reset to", email)
    if form.is_valid():
        form.save(
            subject_template_name=subject_template,
            html_email_template_name=template,
            domain_override=host,
            from_email=settings.NOREPLY_MAIL,
            use_https=True,
        )
        logger.debug("Sent!")
    else:
        logger.warning("Email to %s not sent because form is invalid", str(email))


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