# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM Alarm Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.forms.widgets import HiddenInput, DateTimeInput
from django.utils.dateformat import DateFormat
from django.http import Http404
## NOC modules
from noc.lib.widgets import AutoCompleteTextInput, lookup, TreePopupField
from noc.lib.app import Application, HasPerm, view
from noc.fm.models import *
from noc.sa.models import ManagedObject


class AlarmManagedApplication(Application):
    """
    Alarm manager
    """
    title = "Alarms"
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
    
    def get_alarm_or_404(self, alarm_id):
        """
        Return alarm or raise 404
        """
        a = get_alarm(alarm_id)
        if a:
            return a
        raise Http404("Alarm not found: %s" % alarm_id)

    class AlarmSearchForm(Application.Form):
        """
        Alarm form
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
                                   choices=[("A", "Active"),
                                            ("U", "Unassigned"),
                                            ("O", "Own"),
                                            ("C", "Closed")])
        alarm_class = TreePopupField(label="Alarm Class",
                                     required=False,
                                     document=AlarmClass,
                                     title="Select Alarm Class",
                                     lookup="/fm/alarmclass/popup/")
        order_by = forms.ChoiceField(label="Order by",
                                     required=False,
                                     choices=[
                                            ("-timestamp", "Timestamp"),
                                            ("-severity", "Severity")
                                        ])

    @view(url=r"^$", url_name="index", menu="Alarms", access=HasPerm("view"))
    def view_index(self, request):
        """
        Display alarm list and search form
        """
        initial = {"status": "A", "order_by": "-severity"}
        form = self.AlarmSearchForm(initial=initial)
        return self.render(request, "index.html", form=form)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/$", url_name="alarm",
          access=HasPerm("view"))
    def view_alarm(self, request, alarm_id):
        """
        Display alarm
        """
        def get_chilren(root, level=0):
            children = []
            for a in ActiveAlarm.objects.filter(root=root.id):
                children += [(level, a, a.get_translated_subject(u_lang))]
                children += get_chilren(a, level + 1)
            for a in ArchivedAlarm.objects.filter(root=root.id):
                children += [(level, a, a.get_translated_subject(u_lang))]
                children += get_chilren(a, level + 1)
            return children
        
        alarm = self.get_alarm_or_404(alarm_id)
        root = get_alarm(alarm.root) if alarm.root else None
        u_lang = request.session["django_language"]
        subject = alarm.get_translated_subject(u_lang)
        body = alarm.get_translated_body(u_lang)
        symptoms = alarm.get_translated_symptoms(u_lang)
        probable_causes = alarm.get_translated_probable_causes(u_lang)
        recommended_actions = alarm.get_translated_recommended_actions(u_lang)
        can_clear = alarm.alarm_class.user_clearable
        events = (list(ArchivedEvent.objects.filter(alarms=alarm.id)) +
                  list(ActiveEvent.objects.filter(alarms=alarm.id)))
        events = [(e.id, e.event_class.name,
                   e.timestamp, e.get_translated_subject(u_lang))
                  for e in events]
        severity = AlarmSeverity.get_severity(alarm.severity)
        user = request.user
        is_owner = alarm.status == "A" and alarm.is_owner(user)
        is_subscribed = alarm.status == "A" and alarm.is_subscribed(user)
        is_unassigned = alarm.status == "A" and alarm.is_unassigned
        severities = AlarmSeverity.objects.order_by("severity")
        if alarm.status == "A":
            subscribers = User.objects.filter(id__in=alarm.subscribers).order_by("username")
        else:
            subscribers = []
        children = get_chilren(alarm)  # (level, alarm, subject)
        
        return self.render(request, "alarm.html",
                           a=alarm,
                           root=root,
                           subject=subject,
                           body=body,
                           symptoms=symptoms,
                           probable_causes=probable_causes,
                           recommended_actions=recommended_actions,
                           can_clear=can_clear,
                           events=events,
                           n_events=len(events),
                           severity=severity,
                           is_owner=is_owner,
                           is_subscribed=is_subscribed,
                           is_unassigned=is_unassigned,
                           severities=severities,
                           subscribers=subscribers,
                           children=children,
                           n_children=len(children)
                          )

    class MessageForm(Application.Form):
        message = forms.CharField()

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/message/$", url_name="message",
          access=HasPerm("change"))
    def view_message(self, request, alarm_id):
        """
        Submit new message to event
        """
        alarm = self.get_alarm_or_404(alarm_id)
        if request.POST:
            form = self.MessageForm(request.POST)
            if form.is_valid():
                alarm.log_message("%s: %s" % (request.user.username,
                                              form.cleaned_data["message"]))
                self.message_user(request, "Message posted")
                return self.response_redirect_to_referrer(request)
        self.message_user(request, "Message posting failed")
        return self.response_redirect_to_referrer(request)

    @view(url=r"^alarms/$", url_name="alarms", access=HasPerm("view"))
    def view_alarms(self, request):
        """
        Return JSON list of selected events.
        Returned structure is dict of:
            count:
            page:
            pages:
            alarms: [list_of_alarms]
        """
        datetime_format = self.config.get("main", "datetime_format")
        page = 0
        # Process request
        if request.GET:
            form = self.AlarmSearchForm(request.GET)
            if form.is_valid():
                status = form.cleaned_data["status"]
                # Select alarms collection
                alarms = {
                    "A": ActiveAlarm,
                    "U": ActiveAlarm,
                    "O": ActiveAlarm,
                    "C": ArchivedAlarm
                }[status].objects.filter(root__exists=False)
                #if status == "U":
                #    alarms = alarms.filter(owner__isnull=True)
                if status == "O":
                    alarms = alarms.filter(owner=request.user.id)
                elif status == "U":
                    alarms = alarms.filter(owner=None)
                ## Apply additional restriction
                if form.cleaned_data["page"]:
                    page = form.cleaned_data["page"] - 1
                if form.cleaned_data["from_time"]:
                    alarms = alarms.filter(timestamp__gte=form.cleaned_data["from_time"])
                if form.cleaned_data["to_time"]:
                    alarms = alarms.filter(timestamp__lte=form.cleaned_data["to_time"])
                if form.cleaned_data["managed_object"]:
                    try:
                        mo = ManagedObject.objects.get(name=form.cleaned_data["managed_object"])
                        alarms = alarms.filter(managed_object=mo.id)
                    except ManagedObject.DoesNotExist:
                        pass
                if form.cleaned_data["order_by"]:
                    alarms = alarms.order_by(form.cleaned_data["order_by"])
            else:
                return self.render_json({"error": str(form.errors)})
        lr = self.PAGE_SIZE * page
        rr = self.PAGE_SIZE * (page + 1)
        data = []
        count = alarms.count()
        u_lang = request.session["django_language"]
        for a in alarms[lr:rr]:
            subject = a.get_translated_subject(u_lang)
            alarm_class = a.alarm_class.name
            severity = AlarmSeverity.get_severity(a.severity)
            data += [[
                a.effective_style.css_class_name,
                str(a.id),
                a.managed_object.name,
                DateFormat(a.timestamp).format(datetime_format),
                a.display_duration,
                a.status,
                a.owner.username if a.status == "A" and a.owner else "-",
                alarm_class,
                "%s (%s)" % (severity.name, a.severity),
                subject
            ]]
        return self.render_json({
            "count" : count,
            "page"  : page,
            "pages" : count / self.PAGE_SIZE + (1 if count % self.PAGE_SIZE else 0),
            "alarms": data
            })
    
    @view(url="^css/$", url_name="css", access=HasPerm("view"))
    def view_css(self, request):
        text = "\n\n".join([s.css for s in Style.objects.all()])
        return self.render_plain_text(text, mimetype="text/css")

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/take/$", url_name="take",
          access=HasPerm("change"))
    def view_take(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        if a.status == "A":
            a.change_owner(request.user)
            self.message_user(request, "Alarm has been taken")
        return self.response_redirect_to_referrer(request)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/subscribe/$", url_name="subscribe",
          access=HasPerm("change"))
    def view_subscribe(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        if a.status == "A":
            a.subscribe(request.user)
            self.message_user(request, "You have been subscribed to alarm")
        return self.response_redirect_to_referrer(request)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/unsubscribe/$", url_name="unsubscribe",
          access=HasPerm("change"))
    def view_unsubscribe(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        if a.status == "A":
            a.unsubscribe(request.user)
            self.message_user(request, "You have been unsubscribed from alarm")
        return self.response_redirect_to_referrer(request)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/change_severity/$",
          url_name="change_severity", access=HasPerm("change"))
    def view_change_priority(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        if a.status == "A" and a.owner and a.owner.id == request.user.id and request.GET:
            if "delta" in request.GET:
                delta = int(request.GET.get("delta", 0))
                if delta < -1000 or delta > 1000:
                    delta = 0
                a.change_severity(user=request.user, delta=delta)
                self.message_user(request, "Alarm severity has been changed")
            elif "severity" in request.GET:
                s = AlarmSeverity.objects.filter(id=request.GET["severity"]).first()
                if s:
                    a.change_severity(user=request.user, severity=s)
                    self.message_user(request, "Alarm severity has been changed")
        return self.response_redirect_to_referrer(request)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/clear/$", url_name="clear",
          access=HasPerm("change"))
    def view_clear(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        a.clear_alarm("Cleared by %s" % request.user)
        return self.response_redirect_to_referrer(request)

    @view(url="^(?P<alarm_id>[0-9a-f]{24})/change_root/$",
          url_name="change_root", access=HasPerm("change"))
    def view_change_root(self, request, alarm_id):
        a = self.get_alarm_or_404(alarm_id)
        if request.POST and "root" in request.POST:
            root = request.POST["root"]
            print root
            r = get_alarm(root)
            if r:
                a.set_root(r)
                self.message_user(request, "Root cause has been set")
            else:
                self.message_user(request, "Alarm #%s is not found" % root)
        return self.response_redirect_to_referrer(request)
