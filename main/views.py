from django.shortcuts import render_to_response
import django.contrib.auth
from django.http import HttpResponseRedirect

def index(request):
    return render_to_response("main/index.html")

def logout(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect("/")

def handler404(request):
    return render_to_response("main/404.html")
