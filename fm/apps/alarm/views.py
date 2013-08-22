# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarm application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models import get_alarm, get_event
from noc.sa.models.managedobject import ManagedObject
from noc.main.models import User
from noc.sa.interfaces.base import (ModelParameter, UnicodeParameter,
                                    DateTimeParameter, StringParameter)


class AlarmApplication(ExtApplication):
    """
    fm.alarm application
    """
    title = "Alarm"
    menu = "Alarms"
    icon = "icon_error"

    model_map = {
        "A": ActiveAlarm,
        "C": ArchivedAlarm
    }

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject),
        "timestamp": DateTimeParameter()
    }

    ignored_params = ["status", "_dc"]

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        from plugins.base import AlarmPlugin
        # Load plugins
        self.plugins = {}
        for f in os.listdir("fm/apps/alarm/plugins/"):
            if (not f.endswith(".py") or
                    f == "base.py" or
                    f.startswith("_")):
                continue
            mn = "noc.fm.apps.alarm.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, AlarmPlugin) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
            self.limit_param, self.page_param, self.start_param,
            self.format_param, self.sort_param, self.query_param,
            self.only_param):
            if p in q:
                del q[p]
        # Normalize parameters
        for p in q:
            qp = p.split("__")[0]
            if qp in self.clean_fields:
                q[p] = self.clean_fields[qp].form_clean(q[p])
        #
        if "collapse" in q:
            c = q["collapse"]
            del q["collapse"]
            if c != "0":
                q["root__exists"] = False
        return q

    def instance_to_dict(self, o, fields=None):
        lang = "en"
        s = AlarmSeverity.get_severity(o.severity)
        n_events = (ActiveEvent.objects.filter(alarms=o.id).count() +
                    ArchivedEvent.objects.filter(alarms=o.id).count())
        return {
            "id": str(o.id),
            "status": o.status,
            "managed_object": o.managed_object.id,
            "managed_object__label": o.managed_object.name,
            "severity": s.severity,
            "severity__label": s.name,
            "alarm_class": str(o.alarm_class.id),
            "alarm_class__label": o.alarm_class.name,
            "timestamp": self.to_json(o.timestamp),
            "subject": o.get_translated_subject(lang),
            "events": n_events,
            "duration": o.duration,
            "row_class": s.style.css_class_name
        }

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = request.GET.get("status", "A")
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        return model.objects.all()

    @view(url=r"^$", access="launch", method=["GET"], api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(url=r"^(?P<id>[a-z0-9]{24})/$", method=["GET"], api=True,
          access="launch")
    def api_alarm(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        user = request.user
        lang = "en"
        d = self.instance_to_dict(alarm)
        d["body"] = alarm.get_translated_body(lang)
        d["symptoms"] = alarm.get_translated_symptoms(lang)
        d["probable_causes"] = alarm.get_translated_probable_causes(lang)
        d["recommended_actions"] = alarm.get_translated_recommended_actions(lang)
        d["vars"] = sorted(alarm.vars.items())
        d["status"] = alarm.status
        d["status__label"] = {
            "A": "Active",
            "C": "Cleared"
        }[alarm.status]
        # Managed object properties
        mo = alarm.managed_object
        d["managed_object_address"] = mo.address
        d["managed_object_profile"] = mo.profile_name
        d["managed_object_platform"] = mo.platform
        d["managed_object_version"] = mo.get_attr("version")
        # Log
        if alarm.log:
            d["log"] = [
                {
                    "timestamp": self.to_json(l.timestamp),
                    "from_status": l.from_status,
                    "to_status": l.to_status,
                    "message": l.message
                } for l in alarm.log
            ]
        # Events
        events = []
        for ec in ActiveEvent, ArchivedEvent:
            for e in ec.objects.filter(alarms=alarm.id):
                events += [{
                    "id": str(e.id),
                    "event_class": str(e.event_class.id),
                    "event_class__label": e.event_class.name,
                    "timestamp": self.to_json(e.timestamp),
                    "status": e.status,
                    "managed_object": e.managed_object.id,
                    "managed_object__label": e.managed_object.name,
                    "subject": e.get_translated_subject(lang)
                }]
        if events:
            d["events"] = events
        # Alarms
        children = self.get_nested_alarms(alarm)
        if children:
            d["alarms"] = {
                "expanded": True,
                "children": children
            }
        # Subscribers
        if alarm.status == "A":
            d["subscribers"] = self.get_alarm_subscribers(alarm)
            d["is_subscribed"] = user in alarm.subscribers
        # Apply plugins
        if alarm.alarm_class.plugins:
            plugins = []
            for p in alarm.alarm_class.plugins:
                if p.name in self.plugins:
                    plugin = self.plugins[p.name]
                    dd = plugin.get_data(alarm, p.config)
                    if "plugins" in dd:
                        plugins += dd["plugins"]
                        del dd["plugins"]
                    d.update(dd)
            if plugins:
                d["plugins"] = plugins
        return d

    def get_alarm_subscribers(self, alarm):
        """
        JSON-serializable subscribers
        :param alarm:
        :return:
        """
        subscribers = []
        for u in alarm.subscribers:
            try:
                u = User.objects.get(id=u)
                subscribers += [{
                    "id": u.id,
                    "name": " ".join([u.first_name, u.last_name]),
                    "login": u.username
                }]
            except User.DoesNotExist:
                pass
        return subscribers

    def get_nested_alarms(self, alarm):
        """
        Return nested alarms as a part of NodeInterface
        :param alarm:
        :return:
        """
        children = []
        for ac in (ActiveAlarm, ArchivedAlarm):
            for a in ac.objects.filter(root=alarm.id):
                s = AlarmSeverity.get_severity(a.severity)
                c = {
                    "id": str(a.id),
                    "subject": a.get_translated_subject("en"),
                    "alarm_class": str(a.alarm_class.id),
                    "alarm_class__label": a.alarm_class.name,
                    "managed_object": a.managed_object.id,
                    "managed_object__label": a.managed_object.name,
                    "timestamp": self.to_json(a.timestamp),
                    "iconCls": "icon_error",
                    "row_class": s.style.css_class_name
                }
                nc = self.get_nested_alarms(a)
                if nc:
                    c["children"] = nc
                    c["expanded"] = True
                else:
                    c["leaf"] = True
                children += [c]
        return children

    @view(url=r"^(?P<id>[a-z0-9]{24})/post/", method=["POST"], api=True,
          access="launch", validate={"msg": UnicodeParameter()})
    def api_post(self, request, id, msg):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        alarm.log_message("%s: %s" % (request.user.username, msg))
        return True

    @view(url=r"^(?P<id>[a-z0-9]{24})/subscribe/", method=["POST"],
          api=True, access="launch")
    def api_subscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.subscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        else:
            return []

    @view(url=r"^(?P<id>[a-z0-9]{24})/unsubscribe/", method=["POST"],
          api=True, access="launch")
    def api_unsubscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.unsubscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        else:
            return []

    @view(url=r"^(?P<id>[a-z0-9]{24})/clear/", method=["POST"],
          api=True, access="launch")
    def api_clear(self, request, id):
        alarm = get_alarm(id)
        if alarm.status == "A":
            alarm.clear_alarm("Cleared by %s" % request.user)
        return True

    @view(url=r"^(?P<id>[a-z0-9]{24})/set_root/", method=["POST"],
          api=True, access="launch",
          validate={"root": StringParameter()})
    def api_set_root(self, request, id, root):
        alarm = get_alarm(id)
        r = get_alarm(root)
        if not r:
            return self.response_not_found()
        alarm.set_root(r)
        return True
