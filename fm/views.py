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
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required
from noc.lib.render import render,render_plain_text
from noc.fm.models import Event,EventData,EventClassificationRule,EventClassificationRE,EventPriority, EventClass
from django.http import HttpResponseRedirect,HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import random
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
    def py_q(s):
        return s.replace("\"","\\\"")
    event_class=EventClass.objects.get(id=int(event_class_id))
    s="##\n## %s\n##\n"%event_class.name
    s+="class %s(EventClass):\n"%event_class.name.replace(" ","").replace("-","_")
    s+="    name     = \"%s\"\n"%py_q(event_class.name)
    s+="    category = \"%s\"\n"%py_q(event_class.category.name)
    s+="    priority = \"%s\"\n"%py_q(event_class.default_priority.name)
    s+="    subject_template=\"%s\"\n"%py_q(event_class.subject_template)
    s+="    body_template=\"\"\"%s\"\"\"\n"%event_class.body_template
    vars=list(event_class.eventclassvar_set.all())
    if vars:
        s+="    class Vars:\n"
        for v in event_class.eventclassvar_set.all():
            s+="        %s=Var(required=%s,repeat=%s)\n"%(v.name,v.required,v.repeat_suppression)
    s+="\n"
    return render_plain_text(s)
