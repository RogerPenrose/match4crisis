import logging
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseRedirect

from django.utils.text import format_lazy
from django.utils.translation import gettext as _



from apps.staff.tables import ApprovalOrganisationTable
from apps.iamorganisation.models import Organisation


logger = logging.getLogger(__name__)



@login_required
@staff_member_required
def staff_dashboard(request):
    return render(request, "staff_dashboard.html", {})

    
@login_required
@staff_member_required
def approve_organisations(request):
    table_approved = ApprovalOrganisationTable(Organisation.objects.filter(isApproved=True))
    table_approved.prefix = "approved"
    table_approved.paginate(page=request.GET.get(table_approved.prefix + "page", 1), per_page=5)

    table_unapproved = ApprovalOrganisationTable(Organisation.objects.filter(isApproved=False))
    table_unapproved.prefix = "unapproved"
    table_unapproved.paginate(page=request.GET.get(table_unapproved.prefix + "page", 1), per_page=5)

    return render(
        request,
        "approve_organisations.html",
        {"table_approved": table_approved, "table_unapproved": table_unapproved},
    )


@login_required
@staff_member_required
def change_organisation_approval(request, uuid):

    h = Organisation.objects.get(uuid=uuid)
    logger.info(
        "Set Organisation %s approval to %s", uuid, (not h.isApproved), extra={"request": request},
    )

    if not h.isApproved:
        h.isApproved = True
        h.approval_date = timezone.now()
        h.approved_by = request.user
    else:
        h.isApproved = False
        h.approval_date = None
        h.approved_by = None
    h.save()

    if h.isApproved:
        pass #send_mails_for(h)

    return HttpResponseRedirect("/staff/approve_organisations")


@login_required
@staff_member_required
def delete_organisation(request, uuid):
    h = Organisation.objects.get(uuid=uuid)
    logger.info(
        "Delete Organisation %s by %s", uuid, request.user, extra={"request": request},
    )
    name = h.user
    h.delete()
    text = format_lazy(_("Du hast die Institution mit user '{name}' gelöscht."), name=name)
    messages.add_message(request, messages.INFO, text)
    return HttpResponseRedirect("/staff/approve_organisations")
