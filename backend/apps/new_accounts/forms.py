from django import forms
from django.core.exceptions import ValidationError
import logging
from .models import NewUser

class UserForm(forms.ModelForm):
     class Meta:
        model = NewUser
        fields = ["email", "phoneNumber", "postCode", "userType"]