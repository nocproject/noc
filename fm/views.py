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
from noc.lib.render import render,render_plain_text,render_success,render_failure,render_json
from noc.lib.fileutils import temporary_file
from noc.fm.models import Event,EventData,EventClassificationRule,EventClassificationRE,EventPriority, EventClass,\
    MIB, MIBRequiredException, EventCategory, EVENT_STATUS_CHOICES, EventPostProcessingRule, EventPostProcessingRE, EventCorrelationRule
from noc.sa.models import ManagedObject
from django.http import HttpResponseRedirect,HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
import random,re
from noc.lib.widgets import AutoCompleteTextInput,lookup
from noc.lib.sysutils import refresh_config
from django.forms.widgets import HiddenInput

##
## Returns Managed object names completion
##
@permission_required("fm.change_event")
def lookup_managed_object(request):
    def lookup_function(q):
        for m in ManagedObject.objects.filter(name__istartswith=q):
            yield m.name
    return lookup(request,lookup_function)
##
## Event searching AJAX handler.
## Returns:
## { 
##    count:
##    page:
##    pages:
##    events: [list of events]
## }
##
PAGE_SIZE=20
@permission_required("fm.change_event")
def lookup_events(request):
    events=Event.objects
    page=0
    if request.GET:
        form=EventSearchForm(request.GET)
        if form.is_valid():
            if form.cleaned_data["page"]:
                page=form.cleaned_data["page"]-1
            if form.cleaned_data["from_time"]:
                events=events.filter(timestamp__gte=form.cleaned_data["from_time"])
            if form.cleaned_data["to_time"]:
                events=events.filter(timestamp__lte=form.cleaned_data["to_time"])
            if form.cleaned_data["managed_object"]:
                try:
                    mo=ManagedObject.objects.get(name=form.cleaned_data["managed_object"])
                    events=events.filter(managed_object=mo)
                except ManagedObject.DoesNotExist:
                    pass
            if form.cleaned_data["event_class"]:
                events=events.filter(event_class=form.cleaned_data["event_class"])
            if form.cleaned_data["status"]:
                events=events.filter(status=form.cleaned_data["status"])
            if form.cleaned_data["event_priority"]:
                events=events.filter(event_priority__priority__gte=form.cleaned_data["event_priority"].priority)
            if form.cleaned_data["event_category"]:
                events=events.filter(event_category=form.cleaned_data["event_category"])
            if form.cleaned_data["subject"]:
                events=events.filter(subject__icontains=form.cleaned_data["subject"])
    count=events.count()
    return render_json({
        "count" : count,
        "page"  : page,
        "pages" : count/PAGE_SIZE+(1 if count%PAGE_SIZE else 0),
        "events": [[e.event_priority.css_style_name,e.id,e.managed_object.name,str(e.timestamp),e.status,\
                    e.event_category.name,e.event_class.name,e.event_priority.name,e.subject]\
                    for e in events.order_by("-timestamp")[PAGE_SIZE*page:PAGE_SIZE*(page+1)]]
    }
    )

##
## Event search form
##
class EventSearchForm(forms.Form):
    page=forms.IntegerField(required=False,min_value=0,widget=HiddenInput)
    from_time=forms.DateTimeField(required=False,input_formats=["%d.%m.%Y %H:%M:%S"])
    to_time=forms.DateTimeField(required=False,input_formats=["%d.%m.%Y %H:%M:%S"])
    managed_object=forms.CharField(required=False,widget=AutoCompleteTextInput("/fm/lookup/managed_object/"))
    event_category=forms.ModelChoiceField(required=False,queryset=EventCategory.objects.all())
    event_class=forms.ModelChoiceField(required=False,queryset=EventClass.objects.all())
    status=forms.ChoiceField(required=False,choices=[("","---------")]+EVENT_STATUS_CHOICES)
    event_priority=forms.ModelChoiceField(required=False,queryset=EventPriority.objects.all())
    subject=forms.CharField(required=False)
##
## Display events list scheet
##
@permission_required("fm.change_event")
def index(request):
    initial={"status":"A"}
    try:
        initial["event_priority"]=EventPriority.objects.get(name="WARNING").id
    except EventPriority.DoesNotExist:
        pass
    form=EventSearchForm(initial=initial)
    return render(request,"fm/index.html",{"form":form})
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
def reclassify_event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    event.reclassify_event("Reclassification requested by '%s'"%request.user.username)
    link=request.META.get("HTTP_REFERER","/fm/%d/"%event.id)
    return HttpResponseRedirect(link)
##
## Change event status to Open
##
@permission_required("fm.change_event")
def open_event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    event.open_event("Event opened by '%s'"%request.user.username)
    link=request.META.get("HTTP_REFERER","/fm/%d/"%event.id)
    return HttpResponseRedirect(link)
##
## Change event status to Close
##
@permission_required("fm.change_event")
def close_event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    event.close_event("Event closed by '%s'"%request.user.username)
    link=request.META.get("HTTP_REFERER","/fm/%d/"%event.id)
    return HttpResponseRedirect(link)
##
## Create event classification rule from event
##
@permission_required("fm.add_eventclassificationrule")
def create_rule(request,event_id):
    def re_q(s):
        for qc in ["\\",".","+","*","[","]","(",")"]:
            s=s.replace(qc,"\\"+qc)
        return s
    event=get_object_or_404(Event,id=int(event_id))
    rule=EventClassificationRule(event_class=event.event_class,name="Rule #%d:%d"%(event.id,random.randint(0,100000)),preference=1000)
    rule.save()
    for d in event.eventdata_set.filter(type__in=[">","R"]):
        r=EventClassificationRE(rule=rule,left_re="^%s$"%re_q(d.key)[:254],right_re="^%s$"%re_q(d.value)[:254])
        r.save()
    return HttpResponseRedirect("/admin/fm/eventclassificationrule/%d/"%rule.id)
##
## Clone classification rule from existing one
##
@permission_required("fm.add_eventclassificationrule")
def clone_rule(request,rule_id):
    rule=get_object_or_404(EventClassificationRule,id=int(rule_id))
    # Find suitable rule name
    i=1
    while True:
        name=rule.name+" copy #%d"%i
        try:
            EventClassificationRule.objects.get(name=name)
        except EventClassificationRule.DoesNotExist:
            break
        i+=1
    # Create cloned rule
    new_rule=EventClassificationRule(
        name=name,
        event_class=rule.event_class,
        preference=rule.preference,
        drop_event=rule.drop_event,
        is_builtin=False)
    new_rule.save()
    for r in rule.eventclassificationre_set.all():
        new_r=EventClassificationRE(rule=new_rule,left_re=r.left_re,right_re=r.right_re)
        new_r.save()
    return HttpResponseRedirect("/admin/fm/eventclassificationrule/%d/"%new_rule.id)
##
## Create post-processing rule from event
##
@permission_required("fm.add_eventprostprocessingrule")
def create_postprocessing_rule(request,event_id):
    def re_q(s):
        return s.replace("\\","\\\\").replace(".","\\.").replace("+","\\+").replace("*","\\*")
    event=get_object_or_404(Event,id=int(event_id))
    rule=EventPostProcessingRule(event_class=event.event_class,name="Rule #%d:%d"%(event.id,random.randint(0,100000)),preference=1000)
    rule.save()
    for d in event.eventdata_set.filter(type="V"):
        r=EventPostProcessingRE(rule=rule,var_re="^%s$"%re_q(d.key)[:254],value_re="^%s$"%re_q(d.value)[:254])
        r.save()
    return HttpResponseRedirect("/admin/fm/eventpostprocessingrule/%d/"%rule.id)
##
## Clone post-processing rule
##
@permission_required("fm.add_eventprostprocessingrule")
def clone_postprocessing_rule(request,rule_id):
    rule=get_object_or_404(EventPostProcessingRule,id=int(rule_id))
    # Find suitable rule name
    i=1
    while True:
        name=rule.name+" copy #%d"%i
        try:
            EventPostProcessingRule.objects.get(name=name)
        except EventPostProcessingRule.DoesNotExist:
            break
        i+=1
    # Create cloned rule
    new_rule=EventPostProcessingRule(
        name=name,
        event_class=rule.event_class,
        preference=rule.preference,
        description=rule.description,
        change_priority=rule.change_priority,
        change_category=rule.change_category,
        action=rule.action,
        is_active=True)
    new_rule.save()
    for r in rule.eventpostprocessingre_set.all():
        new_r=EventPostProcessingRE(rule=new_rule,var_re=r.var_re,value_re=r.value_re)
        new_r.save()
    return HttpResponseRedirect("/admin/fm/eventpostprocessingrule/%d/"%new_rule.id)
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
## Convert event correlation rule to python code
##
@permission_required("fm.add_eventcorrelationrule")
def py_event_correlation_rule(request,rule_id):
    rule=get_object_or_404(EventCorrelationRule,id=int(rule_id))
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
##
## Reload noc-classifier config
##
@permission_required("fm.add_eventclassificationrule")
def reload_classifier_config(request):
    referer=request.META.get("HTTP_REFERER","/admin/fm/eventclassificationrule/")
    refresh_config("noc-classifier")
    return HttpResponseRedirect(referer)
##
## Reload noc-correlator config
##
@permission_required("fm.add_eventcorrelationrule")
def reload_correlator_config(request):
    referer=request.META.get("HTTP_REFERER","/admin/fm/eventcorrelationrule/")
    refresh_config("noc-correlator")
    return HttpResponseRedirect(referer)
##
## Active problems summary
##
@permission_required("fm.change_event")
def active_problems_summary(request):
    from django.db import connection
    cursor=connection.cursor()
    cursor.execute("""SELECT o.name AS object_name,ec.name AS class_name,ep.name AS priority_name,COUNT(*) AS count
    FROM fm_event e JOIN sa_managedobject o ON (e.managed_object_id=o.id)
        JOIN fm_eventclass ec ON (ec.id=e.event_class_id)
        JOIN fm_eventpriority ep ON (e.event_priority_id=ep.id)
    WHERE
        e.status='A' AND ep.priority>1000
    GROUP BY 1,2,3
    ORDER BY 1,3,2,4 DESC
    """)
    data=cursor.fetchall()
    return render(request,"fm/active_problems_summary.html",{"data":data})
