# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard views module
## for MAIN module
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import django.contrib.auth
from django.http import HttpResponseRedirect,HttpResponseNotFound
from noc.lib.render import render,render_success,render_failure
from noc.main.report import report_registry
import os
##
## Startup boilerplate
##
def index(request):
    return render(request,"main/index.html")
##
## Log out current user
##
def logout(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect("/")
##
## Called on 404 event
##
def handler404(request):
    return render(request,"main/404.html")
##
## Render report
##
def report(request,report):
    try:
        rc=report_registry[report]
    except KeyError:
        return HttpResponseNotFound("No report found")
    report=rc(request,request.POST)
    if report.is_valid():
        return report.render()
    else:
        return render(request,"main/report_form.html",{"report":report})
##
## Render report list
##
def report_index(request):
    r={}
    for cn,c in report_registry.classes.items():
        m,n=cn.split(".",1)
        if m not in r:
            r[m]=[c]
        else:
            r[m].append(c)
    out=[]
    keys=r.keys()
    keys.sort()
    for k in keys:
        v=r[k]
        v.sort(lambda x,y:cmp(x.title,y.title))
        out.append([k,v])
    return render(request,"main/report_index.html",{"reports":out})
##
## Success page
##
def success(request):
    print request.GET
    subject=request.GET.get("subject",None)
    text=request.GET.get("text",None)
    return render_success(request,subject=subject,text=text)
##
## Failure page
##
def failure(request):
    subject=request.GET.get("subject",None)
    text=request.GET.get("text",None)
    return render_failure(request,subject=subject,text=text)
