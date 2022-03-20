from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables


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
