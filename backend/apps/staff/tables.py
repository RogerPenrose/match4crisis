from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from apps.iamorganisation.models import Organisation


class ContactedTable(tables.Table):
    registration_date = tables.Column(verbose_name=_("E-Mail versendet am"))
    is_activated = tables.Column(empty_values=(), verbose_name=_("Helfer*in noch verfügbar"))
    details = tables.TemplateColumn(template_name="modal_button.html", verbose_name=_(""))

    # TODO: add link to helper detail view to button # noqa: T003
    # helper_info = tables.TemplateColumn(template_name='helper_info_button.html',verbose_name=_(''))

    def render_is_activated(self, value):
        if value:
            text = _("ja")
        else:
            text = _("nein")
        return format_html('<div class="text-center">{}</div>'.format(text))


class OrganisationTable(tables.Table):
    address = tables.Column(accessor='address', verbose_name=_("Adresse"))
    info = tables.TemplateColumn(template_name="info_button.html")

    class Meta:
        model = Organisation
        template_name = "django_tables2/bootstrap4.html"
        fields = ["organisationName", "contactPerson"]
        exclude = ["uuid", "registration_date", "id"]


class ApprovalOrganisationTable(OrganisationTable):
    info = tables.TemplateColumn(template_name="info_button.html")
    status = tables.TemplateColumn(template_name="approval_button.html")
    delete = tables.TemplateColumn(template_name="delete_button.html", verbose_name=_("Löschen"))

    class Meta:
        model = Organisation
        template_name = "django_tables2/bootstrap4.html"
        fields = [
            "organisationName",
            "contactPerson",
            "user__email",
            "user__phoneNumber",
            "user__validatedEmail",
            "approvalDate",
            "approvedBy",
        ]
        exclude = ["uuid", "id", "registration_date"]
        sequence = ("organisationName", "contactPerson", "address", "...", "info", "status", "delete")

