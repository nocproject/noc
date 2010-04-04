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
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseNotFound,HttpResponseForbidden,HttpResponse
from django.db.models.loading import get_model
from django.core.cache import cache
from django.utils.cache import patch_response_headers
from django import forms
from django.views.generic import list_detail
from noc.lib.render import render,render_success,render_failure,render_json
from noc.main.report import report_registry
from noc.main.calculator import calculator_registry
from noc.main.menu import MENU
from noc.main.search import search as search_engine
from noc.main.models import RefBook, RefBookData, TimePattern
import os, types, ConfigParser, pwd, re, time, datetime, csv

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
                elif len(mi)==3 and (mi[2]=="is_logged_user()" and user.is_authenticated()):
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
    format=request.GET.get("format","html")
    report=rc(request,request.POST,format=format)
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
##
##
def calculator(request,calculator):
    try:
        c=calculator_registry[calculator]()
    except KeyError:
        return HttpResponseNotFound("No calculator found")
    return c.render(request)

def calculator_index(request):
    r=[(cn,c.title) for cn,c in calculator_registry.classes.items()]
    r=sorted(r,lambda x,y: cmp(x[1],y[1]))
    return render(request,"main/calculator_index.html",{"calculators":r})
##
## Success page
##
def success(request):
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
CONFIGS=["noc.conf","noc-launcher.conf","noc-fcgi.conf","noc-sae.conf","noc-activator.conf","noc-classifier.conf","noc-correlator.conf","noc-notifier.conf"]

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
    sections=set(conf.sections())
    sections.update(defaults_conf.sections())
    data=[]
    for s in sections:
        options=set()
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
##
## Refbook index
##
def refbook_index(request):
    ref_books=RefBook.objects.filter(is_enabled=True).order_by("name")
    return render(request,"main/refbook_index.html",{"ref_books":ref_books})
##
## Refbook preview
##
def refbook_view(request,refbook_id):
    rb=get_object_or_404(RefBook,id=int(refbook_id))
    can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
    queryset=rb.refbookdata_set.all()
    # Search
    if request.GET and request.GET.has_key("query") and request.GET["query"]:
        query=request.GET["query"]
        # Build query clause
        w=[]
        p=[]
        for f in rb.refbookfield_set.filter(search_method__isnull=False):
            x=f.get_extra(query)
            if not x:
                continue
            w+=x["where"]
            p+=x["params"]
        w=" OR ".join(["(%s)"%x for x in w])
        queryset=queryset.extra(where=["(%s)"%w],params=p)
    else:
        query=""
    # Use generic view for final result
    return list_detail.object_list(
        request,
        queryset=queryset,
        template_name="main/refbook_view.html",
        extra_context={"rb":rb,"can_edit":can_edit,"query":query},
        paginate_by=100,
    )
##
##
##
def refbook_item(request,refbook_id,record_id):
    rb=get_object_or_404(RefBook,id=int(refbook_id))
    rbr=get_object_or_404(RefBookData,id=int(record_id),ref_book=rb)
    can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
    return render(request,"main/refbook_item.html",{"rb":rb,"record":rbr,"can_edit":can_edit})
##
##
##
def refbook_edit(request,refbook_id,record_id=0):
    rb=get_object_or_404(RefBook,id=int(refbook_id))
    rbr=get_object_or_404(RefBookData,id=int(record_id),ref_book=rb)
    can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
    if not can_edit:
        return HttpResponseForbidden("Read-only refbook")
    if request.POST: # Edit refbook
        if not can_edit:
            return HttpResponseForbidden("Read-only refbook")
        # Retrieve record data
        fns=[int(k[6:]) for k in request.POST.keys() if k.startswith("field_")]
        data=["" for i in range(max(fns)+1)]
        for i in fns:
            data[i]=request.POST["field_%d"%i]
        rbr.value=data
        rbr.save()
        return HttpResponseRedirect("/main/refbook/%d/%d/"%(rb.id,rbr.id))
    return render(request,"main/refbook_edit.html",{"rb":rb,"record":rbr})
##
##
##
def refbook_new(request,refbook_id):
    rb=get_object_or_404(RefBook,id=int(refbook_id))
    can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
    if not can_edit:
        return HttpResponseForbidden("Read-only refbook")
    if request.POST: # Edit refbook
        if not can_edit:
            return HttpResponseForbidden("Read-only refbook")
        # Retrieve record data
        fns=[int(k[6:]) for k in request.POST.keys() if k.startswith("field_")]
        data=["" for i in range(max(fns)+1)]
        for i in fns:
            data[i]=request.POST["field_%d"%i]
        rbr=RefBookData(ref_book=rb,value=data)
        rbr.save()
        return HttpResponseRedirect("/main/refbook/%d/%d/"%(rb.id,rbr.id))
    return render(request,"main/refbook_new.html",{"rb":rb})
##
## Delete refbook record
##
def refbook_delete(request,refbook_id,record_id):
    rb=get_object_or_404(RefBook,id=int(refbook_id))
    can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
    if not can_edit:
        return HttpResponseForbidden()
    rbd=get_object_or_404(RefBookData,ref_book=rb,id=int(record_id))
    rbd.delete()
    return HttpResponseRedirect("/main/refbook/%d/"%rb.id)
##
## Test Time Patterns
##
class TestTimePatternsForm(forms.Form):
    time=forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M:%S"])
    
def test_time_patterns(request,time_patterns):
    tp=[get_object_or_404(TimePattern,id=int(x)) for x in time_patterns.split(",")]
    result=[]
    if request.POST:
        form=TestTimePatternsForm(request.POST)
        if form.is_valid():
            t=form.cleaned_data["time"]
            result=[{"pattern":p,"result":p.match(t)} for p in tp]
    else:
        now=datetime.datetime.now()
        s="%02d.%02d.%04d %02d:%02d:%02d"%(now.day,now.month,now.year,now.hour,now.minute,now.second)
        form=TestTimePatternsForm(initial={"time":s})
    return render(request,"main/test_time_patterns.html",{"form":form,"result":result})
##
## CSV Export
##
def csv_export_qs(qs,fields=None):
    model=qs.model
    response=HttpResponse(mimetype="text/csv")
    # response["Content-Disposition"]="attachment;filename=%s.csv"%model.__name__
    writer=csv.writer(response)
    # Write headers
    headers=fields if fields else [f.name for f in model._meta.fields]
    writer.writerow(headers)
    # Dump data
    for obj in qs:
        writer.writerow([unicode(getattr(obj,f)).encode("utf-8") for f in headers])
    # Return CSV
    return response

def admin_list_csv_export(request,app_label,model_name,queryset=None,fields=None):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if not queryset:
        model=get_model(app_label,model_name)
        queryset=model.objects.all()
        filters=dict([(str(k),v) for k,v in request.GET.items() if k not in ("ot","o","p","q")])
        if filters:
            queryset=queryset.filter(**filters)
    return csv_export_qs(queryset, fields)
