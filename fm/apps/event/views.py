# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM event application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.forms.widgets import HiddenInput, DateTimeInput
from django.utils.dateformat import DateFormat
from django.http import Http404
from django.db.models import Q
## NOC modules
from noc.lib.widgets import AutoCompleteTextInput, lookup, TreePopupField
from noc.lib.app import Application, HasPerm, view
from noc.lib.escape import json_escape, fm_escape
from noc.fm.models import *
from noc.sa.models import ManagedObject
from noc.main.models import Checkpoint


class EventAppplication(Application):
    """
    Event manager
    """
    title = "Events"
    ## Amount of events per page
    PAGE_SIZE = 50  # @todo: move to application config

    def get_event_or_404(self, event_id):
        """
        Return event or raise 404
        """
        e = get_event(event_id)
        if e:
            return e
        raise Http404("Event not found: %s" % event_id)

    class EventSearchForm(Application.Form):
        """
        Event filter form
        """
        page = forms.IntegerField(required=False, min_value=0, widget=HiddenInput)
        from_time = forms.DateTimeField(label="From time",
                                        required=False,
                                        input_formats=["%d.%m.%Y %H:%M:%S"],
                                        widget=DateTimeInput(format="%d.%m.%Y %H:%M:%S"))
        to_time = forms.DateTimeField(label="To time",
                                      required=False,
                                      input_formats=["%d.%m.%Y %H:%M:%S"])
        managed_object = forms.CharField(label="Managed Object",
                                         required=False,
                                         widget=AutoCompleteTextInput("sa:managedobject:lookup1"))
        status = forms.ChoiceField(label="Status",
                                   required=False,
                                   choices=[("N", "New"),
                                            ("F", "Failed"),
                                            ("A", "Active"),
                                            ("S", "Archived")])
        event_class = TreePopupField(label="Event Class",
                                     required=False,
                                     document=EventClass,
                                     title="Select Event Class",
                                     lookup="/fm/eventclass/popup/")

    @view(url=r"^$", url_name="index", menu="Events", access=HasPerm("view"))
    def view_index(self, request):
        """
        Display event list and search form
        """
        initial = {"status": "A"}
        form = self.EventSearchForm(initial=initial)
        return self.render(request, "index.html", form=form)

    @view(url="^(?P<event_id>[0-9a-f]{24})/$", url_name="event",
          access=HasPerm("view"))
    def view_event(self, request, event_id):
        """
        Display event
        """
        event = self.get_event_or_404(event_id)
        u_lang = request.session["django_language"]
        if event.status in ("A", "S"):
            subject = event.get_translated_subject(u_lang)
            body = event.get_translated_body(u_lang)
            symptoms = event.get_translated_symptoms(u_lang)
            probable_causes = event.get_translated_probable_causes(u_lang)
            recommended_actions = event.get_translated_recommended_actions(u_lang)
            alarms = [get_alarm(a) for a in event.alarms]
            alarms = [(a.id, a.alarm_class.name, a.timestamp, a.display_duration,
                       a.get_translated_subject(u_lang))
                for a in alarms if a]
            n_alarms = len(alarms)
        else:
            subject = ""
            body = ""
            symptoms = ""
            probable_causes = ""
            recommended_actions = ""
            alarms = None
            n_alarms = 0
        return self.render(request, "event.html", e=event,
                           subject=subject,
                           body=body,
                           symptoms=symptoms,
                           probable_causes=probable_causes,
                           recommended_actions=recommended_actions,
                           alarms=alarms,
                           n_alarms=n_alarms)

    @view(url="^(?P<event_id>[0-9a-f]{24})/reclassify/$", url_name="reclassify",
          access=HasPerm("change"))
    def view_reclassify(self, request, event_id):
        """
        Mark event as new
        """
        event = self.get_event_or_404(event_id)
        if event.status not in ("A", "C", "F"):
            return self.response_forbidden("Invalid event state for requested action")
        event.mark_as_new("Event reclassification has been requested by user %s" % request.user.username)
        self.message_user(request, "Event has been reclassified")
        return self.response_redirect_to_referrer(request)

    class MessageForm(Application.Form):
        message = forms.CharField()

    @view(url="^(?P<event_id>[0-9a-f]{24})/message/$", url_name="message",
          access=HasPerm("change"))
    def view_message(self, request, event_id):
        """
        Submit new message to event
        """
        event = self.get_event_or_404(event_id)
        if request.POST:
            form = self.MessageForm(request.POST)
            if form.is_valid():
                event.log_message("%s: %s" % (request.user.username,
                                              form.cleaned_data["message"]))
                self.message_user(request, "Message posted")
                return self.response_redirect_to_referrer(request)
        self.message_user(request, "Message posting failed")
        return self.response_redirect_to_referrer(request)

    @view(url=r"^events/$", url_name="events", access=HasPerm("view"))
    def view_events(self, request):
        """
        Return JSON list of selected events.
        Returned structure is dict of:
            count:
            page:
            pages:
            events: [list_of_events]
        """
        datetime_format = self.config.get("main", "datetime_format")
        page = 0
        # Process request
        if request.GET:
            form = self.EventSearchForm(request.GET)
            if form.is_valid():
                status = form.cleaned_data["status"]
                # Select event collection
                events = {
                    "N": NewEvent,
                    "A": ActiveEvent,
                    "F": FailedEvent,
                    "S": ArchivedEvent
                }[status].objects
                ## Apply additional restriction
                if form.cleaned_data["page"]:
                    page = form.cleaned_data["page"] - 1
                if form.cleaned_data["from_time"]:
                    events = events.filter(timestamp__gte=form.cleaned_data["from_time"])
                if form.cleaned_data["to_time"]:
                    events = events.filter(timestamp__lte=form.cleaned_data["to_time"])
                if form.cleaned_data["managed_object"]:
                    try:
                        mo = ManagedObject.objects.get(name=form.cleaned_data["managed_object"])
                        events = events.filter(managed_object=mo.id)
                    except ManagedObject.DoesNotExist:
                        pass
                if status in ("A", "C") and "event_class" in form.cleaned_data and form.cleaned_data["event_class"]:
                    events = events.filter(event_class=form.cleaned_data["event_class"].id)
            else:
                return self.render_json({"error": str(form.errors)})
        lr = self.PAGE_SIZE * page
        rr = self.PAGE_SIZE * (page + 1)
        data = []
        
        count = events.count()
        u_lang = request.session["django_language"]
        
        events = list(events.order_by("-timestamp")[lr:rr])
        checkpoints = []
        if events:
            # Get visible checkpoints
            min_time = events[-1].timestamp
            max_time = events[0].timestamp
            q = Q(user=request.user) | Q(private=False)
            cpq = Checkpoint.objects.filter(timestamp__gte=min_time,
                                            timestamp__lte=max_time)
            checkpoints = list(cpq.filter(q).order_by("-timestamp"))
        
        for e in events:
            # Insert checkpoints
            while checkpoints and checkpoints[0].timestamp > e.timestamp:
                cp = checkpoints.pop(0)
                data += [[cp.id, cp.user.username if cp.user else None,
                         DateFormat(cp.timestamp).format(datetime_format),
                         cp.comment]]
            # Insert event
            if e.status in ("A", "S"):
                subject = e.get_translated_subject(u_lang)
                event_class = e.event_class.name
            else:
                subject = ""
                event_class = ""
            data += [[
                str(e.id),
                e.managed_object.name,
                DateFormat(e.timestamp).format(datetime_format),
                e.status,
                event_class,
                subject
            ]]
        return self.render_json({
            "count" : count,
            "page"  : page,
            "pages" : count / self.PAGE_SIZE + (1 if count % self.PAGE_SIZE else 0),
            "events": data
            })
    
    @view(url="^(?P<event_id>[0-9a-f]{24})/to_json/$", url_name="to_json",
          access=HasPerm("view"))
    def view_to_json(self, request, event_id):
        """
        Display event's beef
        """
        event = self.get_event_or_404(event_id)
        vars = event.raw_vars
        keys = []
        lkeys = vars.keys()
        for k in ("source", "profile", "1.3.6.1.6.3.1.1.4.1.0"):
            if k in vars:
                keys += [k]
                lkeys.remove(k)
        keys += sorted(lkeys)
        r = ["["]
        r += ["    {"]
        r += ["        \"profile\": \"%s\"," % json_escape(event.managed_object.profile_name)]
        r += ["        \"raw_vars\": {"]
        x = []
        for k in keys:
            if k in ("collector",):
                continue
            x += ["            \"%s\": \"%s\"" % (json_escape(k),
                                                  json_escape(vars[k]))]
        r += [",\n".join(x)]
        r += ["        }"]
        r += ["    }"]
        r += ["]"]
        return self.render_plain_text("\n".join(r))
