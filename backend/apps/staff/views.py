import logging
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import mpld3

from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect

from django.utils.text import format_lazy
from django.utils.translation import gettext as _

from apps.iamorganisation.models import Organisation
from .models import LetterApprovedBy, Newsletter, NewsletterState
from .forms import NewsletterEditForm, NewsletterViewForm, TestMailForm
from .tables import ApprovalOrganisationTable, NewsletterTable

from .db_stats import DataBaseStats

logger = logging.getLogger(__name__)

matplotlib.use("agg")

def staff_dashboard(request):
    return render(request, "staff_dashboard.html", {})

    
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


def delete_organisation(request, uuid):
    org = Organisation.objects.get(uuid=uuid)
    logger.info(
        "Delete Organisation %s by %s", uuid, request.user, extra={"request": request},
    )
    org.delete()
    text = format_lazy(_("Du hast die Organisation namens '{orgName}' gelöscht."), orgName=org.organisationName)
    messages.add_message(request, messages.INFO, text)
    return HttpResponseRedirect("/staff/approve_organisations")

def confirm_delete(request, uuid):
    request.session['delete_organisation_uuid'] = uuid
    resp = HttpResponseRedirect("#exampleModal1", content = {"uuid" : uuid})
    resp.request = request
    return resp

def switch_newsletter(nl, user, request, post=None, get=None):
    nl_state = nl.sending_state()

    if nl_state == NewsletterState.BEING_EDITED:
        # an edit was made
        if post is not None:
            form = NewsletterEditForm(post, id=nl.id, instance=nl)

            if form.is_valid():
                form.save()
                nl.edit_meta_data(user)
                nl.save()
                messages.add_message(request, messages.INFO, _("Bearbeitungen gespeichert."))
                return switch_newsletter(nl, user, request, post=None, get=None)

        elif get is not None:
            # wants to freeze the form for review
            if "freezeNewsletter" in get:
                nl.freeze(user)
                nl.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    _(
                        "Der Newsletter kann nun nicht mehr editiert werden. Andere Leute können ihn approven."
                    ),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)
            else:
                # the form is a virgin
                form = NewsletterEditForm(id=nl.id, instance=nl)
        else:
            form = NewsletterEditForm(id=nl.id, instance=nl)

    elif nl_state == NewsletterState.UNDER_APPROVAL:
        if get is not None:
            if "unFreezeNewsletter" in get:
                nl.unfreeze()
                nl.save()
                messages.add_message(
                    request, messages.INFO, _("Der Newsletter kann wieder bearbeitet werden."),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)
            elif "approveNewsletter" in get:
                # TODO: check that author cannot approve # noqa: T003
                nl.approve_from(user)
                nl.save()
                messages.add_message(
                    request,
                    messages.WARNING,
                    format_lazy(
                        _(
                            "Noch ist deine Zustimmung UNGÜLTIG. Du musst den Validierungslink in der dir gesendeten Mail ({mail}) anklicken."
                        ),
                        mail=user.email,
                    ),
                )
                approval = LetterApprovedBy.objects.get(newsletter=nl, user=request.user)
                nl.send_approval_mail(approval, host=request.META["HTTP_HOST"])
                switch_newsletter(nl, user, request, post=None, get=None)

        form = NewsletterViewForm(instance=nl)

    elif nl_state == NewsletterState.READY_TO_SEND:
        if get is not None:
            if "sendNewsletter" in get:
                nl.send(user)
                nl.save()
                messages.add_message(request, messages.INFO, _("Der Newsletter wurde versendet."))
                switch_newsletter(nl, user, request)
            if "unFreezeNewsletter" in get:
                nl.unfreeze()
                nl.save()
                messages.add_message(
                    request, messages.INFO, _("Der Newsletter kann wieder bearbeitet werden."),
                )
                return switch_newsletter(nl, user, request, post=None, get=None)

        form = NewsletterViewForm(instance=nl)

    elif nl_state == NewsletterState.SENT:
        form = NewsletterViewForm(instance=nl)
    else:
        from django.http import Http404

        raise Http404

    return form, nl


def view_newsletter(request, id):
    # 404 if not there?
    nl = Newsletter.objects.get(id=id)

    if request.method == "GET" and "email" in request.GET:
        email = request.GET.get("email")
        nl.send_testmail_to(email)
        messages.add_message(
            request, messages.INFO, _("Eine Test Email wurde an %s versendet." % email)
        )

    post = request.POST if request.method == "POST" else None
    get = request.GET if request.method == "GET" else None

    form, nl = switch_newsletter(nl, request.user, request, post=post, get=get)

    # special view if person was the freezer

    context = {
        "form": form,
        "id": id,
        "newsletter_state": nl.sending_state(),
        "state_enum": NewsletterState,
        "mail_form": TestMailForm(),
        "already_approved_by_this_user": nl.has_been_approved_by(request.user),
        "required_approvals": nl.required_approvals(),
        "frozen_by": nl.frozen_by,
        "sent_by": nl.sent_by,
        "send_date": nl.send_date,
        "approvers": ", ".join([a.user.email for a in nl.letterapprovedby_set.all()]),
    }

    return render(request, "newsletter_edit.html", context)


def new_newsletter(request):
    newsletter = Newsletter.objects.create()
    newsletter.letter_authored_by.add(request.user)
    newsletter.save()
    return HttpResponseRedirect("view_newsletter/" + str(newsletter.id))


def list_newsletter(request):
    context = {"table": NewsletterTable(Newsletter.objects.all().order_by("-registration_date"))}
    return render(request, "newsletter_list.html", context)


def did_see_newsletter(request, id, token):
    nl = Newsletter.objects.get(id=id)
    try:
        approval = LetterApprovedBy.objects.get(newsletter=nl, user=request.user)
        if approval.approval_code == int(token):
            approval.did_see_email = True
            approval.save()
            messages.add_message(request, messages.INFO, _("Dein Approval ist nun gültig."))
        else:
            return HttpResponse("Wrong code")
    except Exception:
        return HttpResponse("Not registered")
    return HttpResponseRedirect("/staff/view_newsletter/" + str(id))


def database_stats(request):
    stats = DataBaseStats(length_history_days=14)

    count_stats = stats.all_stats()
    graphs = stats.all_graphs()

    stats_with_plot = []
    for name, history in graphs:
        (x, y) = history
        fig, ax = plt.subplots()
        ax.plot(x, y, "ks-", mec="w", mew=5, ms=17)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(name)
        fig_html = mpld3.fig_to_html(fig)
        stats_with_plot.append((name, fig_html))

    return render(
        request, "database_stats.html", {"count_statistics": count_stats, "graphs": stats_with_plot}
    )
