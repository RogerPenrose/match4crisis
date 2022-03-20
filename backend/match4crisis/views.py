from django.http import HttpResponse
from django.template import loader


def home(request):
    context = {}
    template = loader.get_template("home.html")

    return HttpResponse(template.render(context, request))


def about(request):

    context = {}
    template = loader.get_template("about.html")

    return HttpResponse(template.render(context, request))


def impressum(request):
    context = {}
    template = loader.get_template("impressum.html")

    return HttpResponse(template.render(context, request))


def dataprotection(request):
    context = {}
    template = loader.get_template("dataprotection.html")

    return HttpResponse(template.render(context, request))


def legal_questions(request):
    context = {}
    template = loader.get_template("legal-questions.html")

    return HttpResponse(template.render(context, request))


def terms_of_use(request):
    context = {}
    template = loader.get_template("terms-of-use.html")

    return HttpResponse(template.render(context, request))


def handler404(request, exception=None):
    template = loader.get_template("404.html")
    return HttpResponse(template.render({}, request), status=404)


def handler500(request):
    template = loader.get_template("500.html")
    return HttpResponse(template.render({}, request), status=500)
