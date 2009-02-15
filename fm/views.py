# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard views module
## for FM module
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required
from noc.lib.render import render,render_plain_text,render_success,render_failure
from noc.lib.fileutils import temporary_file
from noc.fm.models import Event,EventData,EventClassificationRule,EventClassificationRE,EventPriority, EventClass, MIB, MIBRequiredException
from django.http import HttpResponseRedirect,HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
import random,re
##
## Display active events list
##
@permission_required("fm.change_event")
def index(request):
    event_list=Event.objects.order_by("-timestamp")
    paginator=Paginator(event_list,100)
    try:
        page=int(request.GET.get("page","1"))
    except ValueError:
        page=1
    try:
        events=paginator.page(page)
    except (EmptyPage,InvalidPage):
        events=paginator.page(paginator.num_pages)
    return render(request,"fm/index.html",{"events":events})
##
## Dynamically generated CSS for event list priorities
##
def event_list_css(request):
    text="\n\n".join([p.css_style for p in EventPriority.objects.all()])
    return HttpResponse(text,mimetype="text/css")
##
## Event preview
##
@permission_required("fm.change_event")
def event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    return render(request,"fm/event.html",{"e":event})
##
## Drop classification mask on event so it can be classified again
##
@permission_required("fm.change_event")
def reclassify(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    event.subject=None
    event.save()
    return HttpResponseRedirect("/fm/%d/"%event.id)
##
## Create event classification rule from event
##
@permission_required("fm.add_eventclassificationrule")
def create_rule(request,event_id):
    def re_q(s):
        return s.replace("\\","\\\\").replace(".","\\.").replace("+","\\+").replace("*","\\*")
    event=get_object_or_404(Event,id=int(event_id))
    rule=EventClassificationRule(event_class=event.event_class,name="Rule #%d:%d"%(event.id,random.randint(0,100000)),preference=1000)
    rule.save()
    for d in event.eventdata_set.filter(type__in=[">","R"]):
        r=EventClassificationRE(rule=rule,left_re="^%s$"%re_q(d.key)[:254],right_re="^%s$"%re_q(d.value))
        r.save()
    return HttpResponseRedirect("/admin/fm/eventclassificationrule/%d/"%rule.id)
##
## Event classification rules overview sheet
##
@permission_required("fm.change_eventclassificationrule")
def view_rules(request):
    return render(request,"fm/view_rules.html",{"rules":EventClassificationRule.objects.order_by("preference")})
##
## Convert event class description to python code
##
@permission_required("fm.add_eventclass")
def py_event_class(request,event_class_id):
    event_class=get_object_or_404(EventClass,id=int(event_class_id))
    return render_plain_text(event_class.python_code)
##
## Convert event classification rule to python code
##
@permission_required("fm.add_eventclassificationrule")
def py_event_classification_rule(request,rule_id):
    rule=get_object_or_404(EventClassificationRule,id=int(rule_id))
    return render_plain_text(rule.python_code)
##
## MIB Upload
##
class MIBUploadForm(forms.Form):
    file=forms.FileField()

@permission_required("fm.add_mib")
def upload_mib(request):
    if request.method=="POST":
        form = MIBUploadForm(request.POST, request.FILES)
        if form.is_valid():
            with temporary_file(request.FILES['file'].read()) as path:
                try:
                    mib=MIB.load(path)
                except MIBRequiredException,x:
                    return render_failure(request,"Failed to upload MIB","%s requires %s"%(x.mib,x.requires_mib))
            return HttpResponseRedirect("/admin/fm/mib/%d/"%mib.id)
    else:
        form=MIBUploadForm()
    return render(request,"fm/mib_upload.html",{"form":form})
