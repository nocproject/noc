# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## <<DESCRIPTION>>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.shortcuts import get_object_or_404
from django.forms.widgets import HiddenInput
from noc.lib.widgets import AutoCompleteTextInput,lookup
from noc.lib.app import Application,HasPerm
from noc.fm.models import *
from noc.sa.models import ManagedObject
from django.utils.dateformat import DateFormat
##
## Event Manager
##
class EventAppplication(Application):
    title="Events"
    ## Amount of events per page
    PAGE_SIZE=20
    ##
    ## Event search form
    ##
    class EventSearchForm(Application.Form):
        page=forms.IntegerField(required=False,min_value=0,widget=HiddenInput)
        from_time=forms.DateTimeField(required=False,input_formats=["%d.%m.%Y %H:%M:%S"])
        to_time=forms.DateTimeField(required=False,input_formats=["%d.%m.%Y %H:%M:%S"])
        managed_object=forms.CharField(required=False,widget=AutoCompleteTextInput("sa:managedobject:lookup"))
        event_category=forms.ModelChoiceField(required=False,queryset=EventCategory.objects.all())
        event_class=forms.ModelChoiceField(required=False,queryset=EventClass.objects.all())
        status=forms.ChoiceField(required=False,choices=[("","---------")]+EVENT_STATUS_CHOICES)
        event_priority=forms.ModelChoiceField(required=False,queryset=EventPriority.objects.all())
        subject=forms.CharField(required=False)
    ##
    ## Display event list
    ##
    def view_index(self,request):
        initial={"status":"A"}
        try:
            initial["event_priority"]=EventPriority.objects.get(name="WARNING").id
        except EventPriority.DoesNotExist:
            pass
        form=self.EventSearchForm(initial=initial)
        return self.render(request,"index.html",{"form":form})
    view_index.url=r"^$"
    view_index.access=HasPerm("view")
    view_index.menu="Events"
    ##
    ## Display event colorification CSS
    ## <!> use cache
    def view_css(self,request):
        text="\n\n".join([p.css_style for p in EventPriority.objects.all()])
        return self.render_plain_text(text,mimetype="text/css")
    view_css.url=r"css/$"
    view_css.url_name="css"
    view_css.access=HasPerm("view")
    ##
    ## Display event
    ##
    def view_event(self,request,event_id):
        event=get_object_or_404(Event,id=int(event_id))
        return self.render(request,"event.html",{"e":event})
    view_event.url=r"^(?P<event_id>\d+)/$"
    view_event.url_name="event"
    view_event.access=HasPerm("view")
    ##
    ## Mark event as open
    ##
    def view_open(self,request,event_id):
        event=get_object_or_404(Event,id=int(event_id))
        event.open_event("Event opened by '%s'"%request.user.username)
        return self.response_redirect_to_referrer(request,self.base_url+"%d/"%event.id)
    view_open.url=r"^(?P<event_id>\d+)/open/$"
    view_open.url_name="open"
    view_open.access=HasPerm("change")
    ##
    ## Mark event as closed
    ##
    def view_close(self,request,event_id):
        event=get_object_or_404(Event,id=int(event_id))
        event.close_event("Event closed by '%s'"%request.user.username)
        return self.response_redirect_to_referrer(request,self.base_url+"%d/"%event.id)
    view_close.url=r"^(?P<event_id>\d+)/close/$"
    view_close.url_name="close"
    view_close.access=HasPerm("close")
    ##
    ## Begin event reclassification
    ##
    def view_reclassify(self,request,event_id):
        event=get_object_or_404(Event,id=int(event_id))
        event.reclassify_event("Reclassification requested by '%s'"%request.user.username)
        return self.response_redirect_to_referrer(request,self.base_url+"%d/"%event.id)
    view_reclassify.url=r"^(?P<event_id>\d+)/reclassify/$"
    view_reclassify.url_name="reclassify"
    view_reclassify.access=HasPerm("reclassify")
    ##
    ## Retrieve JSON list of events
    ## Returns:
    ## { 
    ##    count:
    ##    page:
    ##    pages:
    ##    events: [list of events]
    ##
    def view_events(self,request):
        datetime_format=self.config.get("main","datetime_format")
        events=Event.objects
        page=0
        if request.GET:
            form=self.EventSearchForm(request.GET)
            if form.is_valid():
                ## Apply additional restriction
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
        # Return list of events
        count=events.count()
        return self.render_json({
            "count" : count,
            "page"  : page,
            "pages" : count/self.PAGE_SIZE+(1 if count%self.PAGE_SIZE else 0),
            "events": [[e.event_priority.css_style_name,e.id,e.managed_object.name,DateFormat(e.timestamp).format(datetime_format),
                        e.status,
                        e.event_category.name,e.event_class.name,e.event_priority.name,e.subject]
                        for e in events.order_by("-timestamp")[self.PAGE_SIZE*page:self.PAGE_SIZE*(page+1)]]
        })
    view_events.url=r"^events/$"
    view_events.url_name="events"
    view_events.access=HasPerm("view")
