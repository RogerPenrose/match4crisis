from django.shortcuts import render

from apps.accounts.views import DashboardView

def thx(request):
    return render(request, "thanks.html")

class HelperDashboardView(DashboardView):
    template_name = "helper_dashboard.html"

    
