from django.shortcuts import render

# Create your views here.

def thx(request):
    return render(request, "thanks.html")