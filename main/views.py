import django.contrib.auth
from django.http import HttpResponseRedirect
from noc.lib.render import render

def index(request):
    return render(request,"main/index.html")

def logout(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect("/")

def handler404(request):
    return render_to_response("main/404.html")
