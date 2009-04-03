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
from django.core.cache import cache
from django.utils.cache import patch_response_headers
from django import forms
from noc.lib.render import render,render_success,render_failure,render_json
from noc.main.report import report_registry
from noc.main.menu import MENU
from noc.main.search import search as search_engine
import os, types
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
## Returns JSON with user's menu
##
MENU_CACHE_TIME=600 # Should be settable from config
def menu(request):
    cache_key="menu:%d"%request.user.id
    menu=cache.get(cache_key)
    if menu is None:
        menu=[]
        user=request.user
        for m in MENU:
            r=[]
            for mi in m["items"]:
                if len(mi)==3 and user.has_perm(mi[2]):
                    r+=[(mi[0],mi[1])]
                elif type(mi[1])==types.DictType:
                    sr=[(x[0],x[1]) for x in mi[1]["items"] if len(x)==2 or user.has_perm(x[2])]
                    if sr:
                        r+=[(mi[0],{"items":sr})]
            if r:
                mi={"items":r}
                for k,v in m.items():
                    if k=="items":
                        continue
                    mi[k]=v
                menu.append(mi)
        cache.set(cache_key,menu,MENU_CACHE_TIME)
    response=render_json(menu)
    patch_response_headers(response,MENU_CACHE_TIME)
    return response
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
##
## Search engine
##
class SearchForm(forms.Form):
    query=forms.CharField()
    
def search(request):
    result=[]
    if request.POST:
        form=SearchForm(request.POST)
        if form.is_valid():
            result=search_engine(request.user,form.cleaned_data["query"])
    else:
        form=SearchForm()
    return render(request,"main/search.html",{"form":form,"result":result})
