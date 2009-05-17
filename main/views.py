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
from __future__ import with_statement
import django.contrib.auth
from django.http import HttpResponseRedirect,HttpResponseNotFound,HttpResponseForbidden
from django.core.cache import cache
from django.utils.cache import patch_response_headers
from django import forms
from noc.lib.render import render,render_success,render_failure,render_json
from noc.main.report import report_registry
from noc.main.menu import MENU
from noc.main.search import search as search_engine
import os, types, ConfigParser, sets, pwd, re
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
                if len(mi)==3 and ((mi[2]=="is_superuser()" and user.is_superuser) or (mi[2]!="is_superuser()" and user.has_perm(mi[2]))):
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
##
## Configuration editor
##
CONFIGS=["noc.conf","noc-sae.conf","noc-activator.conf","noc-classifier.conf"]

def config_index(request):
    config_list=CONFIGS[:]
    return render(request,"main/config_index.html",{"configs":config_list})
##
## Edit configs
##
def config_view(request,config):
    def encode_name(section,name):
        return "%s::%s"%(section,name)
    def decode_name(name):
        return name.split("::")
    if not request.user.is_superuser:
        return HttpResponseForbidden("Super-User privileges required")
    if config not in CONFIGS:
        return HttpResponseNotFound("%s not found"%config)
    if request.POST:
        ##
        ## Attempt to save config
        ##
        conf=ConfigParser.RawConfigParser()
        for name,value in request.POST.items():
            if not value:
                continue
            section,option=decode_name(name)
            if not conf.has_section(section):
                conf.add_section(section)
            conf.set(section,option,value)
        with open("etc/%s"%config,"w") as f:
            conf.write(f)
        return HttpResponseRedirect("/main/config/%s/"%config)
    ##
    ## Search for available online help
    ##
    help_path="static/doc/en/ug/html/_sources/configuration.txt"
    help_prefix=config.replace(".","-")
    help_href="/static/doc/en/ug/html/configuration.html#%s"
    with open(help_path) as f:
        help=f.read()
    rx=re.compile(r"^\.\. _(%s.*?):"%help_prefix,re.MULTILINE)
    help=[x.replace("_","-") for x in rx.findall(help)]
    ##
    ## Read config data
    ##
    conf=ConfigParser.RawConfigParser()
    conf.read("etc/%s"%config)
    read_only=not os.access("etc/%s"%config,os.W_OK)
    system_user=pwd.getpwuid(os.getuid())[0]
    defaults_conf=ConfigParser.RawConfigParser()
    defaults_conf.read("etc/%s.defaults"%config[:-5])
    sections=sets.Set(conf.sections())
    sections.update(defaults_conf.sections())
    data=[]
    for s in sections:
        options=sets.Set()
        if conf.has_section(s):
            options.update(conf.options(s))
        if defaults_conf.has_section(s):
            options.update(defaults_conf.options(s))
        sd=[]
        for o in options:
            x={"name":encode_name(s,o),"label":o}
            if conf.has_option(s,o):
                x["value"]=conf.get(s,o)
            else:
                x["value"]=""
            if defaults_conf.has_option(s,o):
                x["default"]=defaults_conf.get(s,o)
            else:
                x["default"]=""
            # Try to find online help for option and determine option order
            option_help="%s-%s-%s"%(help_prefix,s.replace("_","-"),o.replace("_","-"))
            try:
                x["index"]=help.index(option_help)
                x["help"]=help_href%option_help
            except ValueError:
                x["index"]=10000
                x["help"]=None
            sd.append(x)
        # Order options like manual
        sd=sorted(sd,lambda x,y:cmp(x["index"],y["index"]))
        # Try to find online help for section and determine section order
        section_help="%s-%s"%(help_prefix,s.replace("_","-"))
        try:
            index=help.index(section_help)
            section_help=help_href%section_help
        except ValueError:
            index=10000
            section_help=None
        data.append({"section":s,"data":sd,"help":section_help,"index":index})
    # Order sections like manual
    data=sorted(data,lambda x,y:cmp(x["index"],y["index"]))
    return render(request,"main/config_view.html",{"config_name":config,"data":data,
        "read_only":read_only,"system_user":system_user})
