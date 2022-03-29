from django.shortcuts import render

from apps.accounts.views import DashboardView

# Create your views here.

def thx(request):
    return render(request, "thanks.html")

class RefugeeDashboardView(DashboardView):
    template_name = "refugee_dashboard.html"
