import django.contrib.auth
from django.http import HttpResponseRedirect,HttpResponseNotFound
from noc.lib.render import render
from noc.main.report import get_report_class,report_classes
import os

def index(request):
    return render(request,"main/index.html")

def logout(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect("/")

def handler404(request):
    return render(request,"main/404.html")

def report(request,module,report):
    if "." in module or os.sep in module:
        return HttpResponseNotFound("No module")
    if "." in report or os.sep in report:
        return HttpResponseNotFound("No report")
    try:
        rc=get_report_class(module,report)
    except KeyError:
        return HttpResponseNotFound("No report found")
    report=rc(request,request.POST)
    if report.is_valid():
        return report.render()
    else:
        return render(request,"main/report_form.html",{"report":report})

def report_index(request):
    return render(request,"main/report_index.html",{"reports":report_classes})