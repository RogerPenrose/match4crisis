from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import LanguageKnowledge, Languages, User


class LanguageKnowledgeInline(admin.TabularInline):
    model = LanguageKnowledge
    extra = 1

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phoneNumber', 'sharePhoneNumber')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'phoneNumber', 'is_staff')
    list_filter = ('is_staff', 'isHelper', 'isRefugee', 'isOrganisation', 'is_active', 'validatedEmail')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (LanguageKnowledgeInline,)

@admin.register(Languages)
class LanguagesAdmin(admin.ModelAdmin):
    ordering = ('isoCode',)
    list_display = ('englishName', 'nativeName', 'isoCode', 'country')
